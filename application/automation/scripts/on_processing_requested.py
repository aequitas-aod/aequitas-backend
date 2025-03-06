import copy
import io
import random
from typing import Iterable, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas.plotting import parallel_coordinates
from sklearn.metrics import get_scorer
from sklearn.model_selection import StratifiedKFold

from resources.db.datasets import dataset_path

import utils.env
from application.automation.parsing import read_csv, to_csv, to_json
from application.automation.setup import Automator
from application.automation.scripts.on_dataset_created import (
    get_heads,
    get_stats,
)
from application.automation.scripts.on_dataset_features_available import (
    metrics as generate_metrics,
    correlation_matrix_picture,
)
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import set_other_loggers_level

from aif360.algorithms.preprocessing import LFR
from fairlearn.preprocessing import CorrelationRemover
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OrdinalEncoder
from aif360.datasets import BinaryLabelDataset
from fairlearn import metrics as fairlearn_metrics

import warnings


FIG_WIDTH_SIZE = 12
FIG_HEIGHT_SIZE = 5
FIG_DPI = 300
PREPROCESSING_SAMPLE_SIZE = 200

FIG_WIDTH_SIZE = 12
FIG_HEIGHT_SIZE = 5
FIG_DPI = 300


# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()


class AbstractProcessingRequestedReaction(Automator):
    def __init__(self, *phases):
        super().__init__(["processing.requested"])
        self.__supported_phases = set(phases)

    @property
    def supported_phases(self):
        return tuple(self.__supported_phases)

    # noinspection PyMethodOverriding
    def on_event(
        self,
        topic: str,
        project_id: EntityId,
        project: Project,
        context_key: str,
        phase: str,
    ):
        if phase not in self.__supported_phases:
            self.log(
                "Ignoring event %s, because it is related to phase %s and this automator only supports phases %s",
                topic,
                phase,
                self.__supported_phases,
            )
            return
        dataset_id: str = context_key.split("__")[1]
        dataset: pd.DataFrame = self.get_from_context(
            project_id, f"dataset__{dataset_id}", "csv"
        )
        features: dict = self.get_from_context(
            project_id, f"features__{dataset_id}", "json"
        )
        drops = {key for key, value in features.items() if value["drop"]}
        targets = {
            key
            for key, value in features.items()
            if value["target"]
            if key not in drops
        }
        sensitive = {
            key
            for key, value in features.items()
            if value["sensitive"]
            if key not in drops
        }
        proxies = self.get_from_context(project_id, f"proxies__{dataset_id}", "json")
        detected = self.get_from_context(project_id, f"detected__{dataset_id}", "json")
        if isinstance(detected, dict):
            metrics = list(detected.keys())
            selected_targets = [
                v["target"]
                for _, v in detected.items()
                if isinstance(v, dict) and "target" in v and v["target"] in targets
            ] or list(targets)
            selected_sensitives = [
                v["sensitive"]
                for _, v in detected.items()
                if isinstance(v, dict)
                and "sensitive" in v
                and v["sensitive"] in sensitive
            ] or list(sensitive)
        else:
            metrics = []
            selected_targets = list(targets)
            selected_sensitives = list(sensitive)
        hyperparameters = self.get_from_context(project_id, context_key, "json")
        processing_history = (
            self.get_from_context(
                project_id, f"processing_history", "json", optional=True
            )
            or []
        )
        algorithm = hyperparameters["$algorithm"]
        self.log(
            "Requested %sprocessing with algorithm %s for dataset %s with metrics=%s, sensitives=%s, targets=%s",
            phase,
            algorithm,
            dataset_id,
            metrics,
            selected_sensitives,
            selected_targets,
        )
        processing_history.append(
            dict(phase=phase, dataset=dataset_id, algorithm=algorithm)
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for k, v in self.produce_info(
                phase,
                dataset_id,
                dataset,
                metrics,
                selected_targets,
                selected_sensitives,
                proxies,
                detected,
                hyperparameters,
            ):
                self.update_context(project_id, k, v)
        self.update_context(project_id, processing_history=to_json(processing_history))

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        metrics: list[str],
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def next_name(dataset_id: str) -> str:
        if "-" in dataset_id:
            last = dataset_id.split("-")[-1]
            try:
                index = int(last)
                return dataset_id[: -len(last)] + str(index + 1)
            except ValueError:
                pass
        return dataset_id + "-1"

    def _call_global_algorithm(
        self,
        dataset: pd.DataFrame,
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
        prefix: str = None,
    ):
        if prefix is None:
            prefix = self.supported_phases[0]
        algorithm = hyperparameters.pop("$algorithm")
        function_name = f"{prefix}processing_algorithm_{algorithm}"
        if function_name not in globals():
            raise KeyError("No such algorithm: %s" % algorithm)
        function = globals()[function_name]
        self.log(
            "Executing %s: \n"
            "\ton dataset of shape %s\n"
            "\twith sensitive attributes %s\n"
            "\tand targets %s\n"
            "\twith hyperparameters %s",
            algorithm,
            dataset.shape,
            sensitive,
            targets,
            hyperparameters,
        )
        result = function(
            dataset,
            sensitive,
            targets,
            proxies=proxies,
            detected=detected,
            **hyperparameters,
        )
        self.log(
            "Executed %s: result is of type %s",
            algorithm,
            type(result),
        )
        return algorithm, result


class AIF360PreprocWrapper(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        aif360_model,
        sensitive_feature,
        favorable_class_label,
        unfavorable_class_label,
        favorable_sens_group,
        unfavorable_sens_group,
    ):
        self.aif360_model = aif360_model

        self.sensitive_feature = sensitive_feature
        self.favorable_sens_group = favorable_sens_group
        self.unfavorable_sens_group = unfavorable_sens_group

        self.class_feature = "label"
        self.favorable_class_label = favorable_class_label
        self.unfavorable_class_label = unfavorable_class_label

        self.ordinal_encoder = None

    def _encode_features(self, df, fit):

        df_encoded = df.copy()

        # Encode class
        if self.class_feature in df_encoded.columns:
            df_encoded[self.class_feature] = df_encoded[self.class_feature].apply(
                lambda x: 1 if x == self.favorable_class_label else 0
            )
        else:
            df_encoded[self.class_feature] = 0  # or any constant value

        # Encode sensitive feature
        if (
            self.sensitive_feature
            in df_encoded.select_dtypes(include=["object", "category"]).columns
        ):
            df_encoded[self.sensitive_feature] = df_encoded[
                self.sensitive_feature
            ].apply(lambda x: 1 if x == self.favorable_sens_group else 0)

        # Encode other columns
        categorical_cols = df_encoded.select_dtypes(
            include=["object", "category"]
        ).columns
        numeric_cols = df_encoded.select_dtypes(exclude=["object", "category"]).columns

        if fit:
            self.ordinal_encoder = OrdinalEncoder()
            self.ordinal_encoder.fit(df_encoded[categorical_cols])

        if len(categorical_cols) > 0:
            df_encoded[categorical_cols] = self.ordinal_encoder.transform(
                df_encoded[categorical_cols]
            )
        if len(numeric_cols) > 0:
            df_encoded[numeric_cols] = df_encoded[numeric_cols]

        # Check missing values
        # print(df_encoded.isna().sum())
        # df_encoded = df_encoded.set_index(self.sensitive_feature)
        # print(df_encoded.isna().sum())
        # print(df_encoded)

        return df_encoded

    def fit(self, X, y, **kwargs):
        if not self.sensitive_feature:
            raise ValueError("Protected attribute name must be specified.")

        df_encoded = self._encode_features(df=X.assign(label=y), fit=True)

        # print(df_encoded)
        dataset = BinaryLabelDataset(
            df=df_encoded,
            label_names=[self.class_feature],
            # sensitive_features=[self.sensitive_feature],
            protected_attribute_names=[self.sensitive_feature],
            favorable_label=1,
            unfavorable_label=0,
        )
        self.aif360_model = self.aif360_model.fit(dataset, **kwargs)
        return self

    def transform(self, X, decode=False):
        X_encoded = self._encode_features(df=X, fit=False)
        dataset = BinaryLabelDataset(
            df=X_encoded,
            label_names=[self.class_feature],
            # sensitive_features=[self.sensitive_feature],
            protected_attribute_names=[self.sensitive_feature],
            favorable_label=1,
            unfavorable_label=0,
        )
        new_X = self.aif360_model.transform(dataset).convert_to_dataframe()[0]
        new_X[self.sensitive_feature] = (
            new_X[self.sensitive_feature].apply(
                lambda x: (
                    self.favorable_sens_group if x == 1 else self.unfavorable_sens_group
                )
            )
            if decode
            else new_X[self.sensitive_feature]
        )
        return new_X


def _get_default_settings(sensitive: list[str], targets: list[str]) -> dict:

    sensitive_feat = sensitive[0]
    target_feat = targets[0]

    if sensitive_feat == "f_ESCS":
        favorable_sensitive_label = "OTHERS"
        unfavorable_sensitive_label = "DISADVANTAGED"

        favorable_class_label = "PASSING"
        unfavorable_class_label = "AT RISK"
    else:
        favorable_sensitive_label = "Male"
        unfavorable_sensitive_label = "Female"

        favorable_class_label = ">50K"
        unfavorable_class_label = "<=50K"

    return {
        # sensitive variables
        "sensitive_feat": sensitive_feat,
        "favorable_sensitive_label": favorable_sensitive_label,
        "unfavorable_sensitive_label": unfavorable_sensitive_label,
        # target variables
        "target_feat": target_feat,
        "favorable_class_label": favorable_class_label,
        "unfavorable_class_label": unfavorable_class_label,
        "predictions_feat": "predictions",
    }


def _discretize_columns(df: pd.DataFrame) -> pd.DataFrame:
    encoded_df = copy.deepcopy(df)
    categorical_features = encoded_df.select_dtypes(
        include=["object", "category"]
    ).columns

    # Apply Ordinal Encoding
    encoder = OrdinalEncoder()
    encoded_df[categorical_features] = encoder.fit_transform(
        encoded_df[categorical_features]
    )
    return encoded_df


def _filter_keys(data: dict, *keys):
    keys = set(keys)
    return {k: v for k, v in data.items() if k in keys}


def preprocessing_algorithm_LearnedFairRepresentations(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    default_settings = _get_default_settings(sensitive=sensitive, targets=targets)
    if default_settings["sensitive_feat"] == "f_ESCS":
        return pd.read_csv(dataset_path("preprocessed_lfr_result_ull"))
    else:
        X, y = (
            dataset[
                [
                    col
                    for col in dataset.columns
                    if col != default_settings["target_feat"]
                ]
            ],
            dataset[default_settings["target_feat"]],
        )

        mitigator = LFR(
            unprivileged_groups=[{default_settings["sensitive_feat"]: 0}],
            privileged_groups=[{default_settings["sensitive_feat"]: 1}],
            **_filter_keys(kwargs, "k", "Ax", "Ay", "Az", "seed"),
            seed=0,
        )
        wrapper = AIF360PreprocWrapper(
            aif360_model=mitigator,
            sensitive_feature=default_settings["sensitive_feat"],
            favorable_sens_group=default_settings["favorable_sensitive_label"],
            unfavorable_sens_group=default_settings["unfavorable_sensitive_label"],
            favorable_class_label=default_settings["favorable_class_label"],
            unfavorable_class_label=default_settings["unfavorable_class_label"],
        )

        wrapper.fit(X, y)
        X_t = wrapper.transform(X, decode=True)
        transformed_df = pd.concat(
            [
                X_t.reset_index(drop=True).drop("label", axis=1),
                y.reset_index(drop=True),
            ],
            axis=1,
        )

        return transformed_df


def preprocessing_algorithm_DisparateImpactRemover(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    # TODO: @josephgiovanelli add implementation
    return dataset


def preprocessing_algorithm_Reweighing(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    # TODO: @josephgiovanelli add implementation
    return dataset


def preprocessing_algorithm_CorrelationRemover(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    default_settings = _get_default_settings(sensitive=sensitive, targets=targets)

    X, y = (
        dataset[
            [col for col in dataset.columns if col != default_settings["target_feat"]]
        ],
        dataset[default_settings["target_feat"]],
    )

    feature_names = X.columns
    selected_sensitive_index = [
        idx
        for idx, elem in enumerate(feature_names)
        if default_settings["sensitive_feat"] == elem
    ]
    corr_remover = CorrelationRemover(
        sensitive_feature_ids=selected_sensitive_index, **_filter_keys(kwargs, "alpha")
    )
    X_t = corr_remover.fit_transform(_discretize_columns(X).to_numpy(), y.to_numpy)
    transformed_df = pd.concat(
        [
            pd.DataFrame(
                X_t,
                columns=[
                    elem
                    for elem in feature_names
                    if elem != default_settings["sensitive_feat"]
                ],
            ),
            X[default_settings["sensitive_feat"]].reset_index(drop=True),
            y.reset_index(drop=True),
        ],
        axis=1,
    )
    return transformed_df


def inprocessing_algorithm_no_mitigation(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:

    def __simulate_mit_value(metric_name: str) -> float:
        if metric_name == "accuracy":
            return _generate_random_number(0.8, 0.9)
        elif metric_name == "precision":
            return _generate_random_number(0.85, 0.9)
        elif metric_name == "recall":
            return _generate_random_number(0.75, 0.8)
        elif metric_name == "roc_auc":
            return _generate_random_number(0.75, 0.8)
        elif metric_name == "f1":
            return _generate_random_number(0.75, 0.85)
        elif metric_name == "demographic_parity_ratio":
            return _generate_random_number(0.8, 0.9)
        elif metric_name == "equalized_odds_ratio":
            return _generate_random_number(0.75, 0.85)
        else:
            return 0.5

    def __simulate_no_mit_value(
        metric_type: str, metric_name: str, actual_value: float
    ) -> float:
        if metric_type == "performance":
            if metric_name not in ["recall", "roc_auc", "f1"]:
                return min(actual_value + _generate_random_number(0.01, 0.07), 0.95)
            elif metric_name == "recall":
                return actual_value - _generate_random_number(0.05, 0.07)
            else:
                return actual_value - _generate_random_number(0.01, 0.05)
        elif metric_type == "fairness":
            return max(actual_value - _generate_random_number(0.2, 0.25), 0.0)
        else:
            return actual_value

    def __simulate_polarized_value(metric_type: str, actual_value: float) -> float:
        if metric_type == "performance":
            return min(actual_value - _generate_random_number(0.2, 0.25), 1.0)
        elif metric_type == "fairness":
            return max(actual_value - _generate_random_number(0.2, 0.25), 0.0)
        else:
            return actual_value

    default_settings = _get_default_settings(sensitive=sensitive, targets=targets)

    X, y = (
        dataset[
            [col for col in dataset.columns if col != default_settings["target_feat"]]
        ],
        dataset[default_settings["target_feat"]],
    )

    skf = StratifiedKFold(n_splits=5)

    # Prepare list for 1) and 2)
    df_results = []  # list of dicts; one dict per fold-metric

    perf_metrics = ["accuracy", "precision", "recall", "roc_auc", "f1"]
    fair_metrics = ["demographic_parity_ratio", "equalized_odds_ratio"]
    support_dict = {"performance": perf_metrics, "fairness": fair_metrics}

    # Evaluation loop
    for fold_idx, (train_index, test_index) in enumerate(skf.split(X, y)):
        for metric_type, metric_list in support_dict.items():
            for metric_name in metric_list:
                mit_value = __simulate_mit_value(metric_name)
                no_mit_value = __simulate_no_mit_value(
                    metric_type, metric_name, mit_value
                )
                pol_value = __simulate_polarized_value(metric_type, no_mit_value)

                df_results.append(
                    {
                        "fold": fold_idx,
                        "metric_type": metric_type,
                        "metric": metric_name.replace("_", " ").title(),
                        "value_mitig": mit_value,
                        "value_nomitig": no_mit_value,
                        "value_pol": pol_value,
                    }
                )

    return pd.DataFrame(df_results)


def generate_preprocessing_plot_picture(
    transformed_dataset: pd.DataFrame, file: io.BytesIO, **kwargs
):
    final_sample = (
        _discretize_columns(kwargs["original_dataset"])
        .drop(kwargs["class_feature"], axis=1)
        .reset_index(drop=True)
        .sample(
            n=min(PREPROCESSING_SAMPLE_SIZE, len(kwargs["original_dataset"])),
            random_state=42,
        )
        .copy()
    )
    trans_sample = (
        _discretize_columns(transformed_dataset)
        .drop(kwargs["class_feature"], axis=1)
        .reset_index(drop=True)
        .sample(
            n=min(PREPROCESSING_SAMPLE_SIZE, len(transformed_dataset)), random_state=42
        )
        .copy()
    )

    # 3) Tag each subset with a "source"
    final_sample["source"] = "Original"
    trans_sample["source"] = "Transformed"

    # 4) Concatenate them
    combined = pd.concat([final_sample, trans_sample], ignore_index=True)

    # 5) Parallel Coordinates expects one categorical column (here "source") to color the lines
    plt.figure(figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE))
    parallel_coordinates(
        combined,
        class_column="source",
        color=["blue", "red"],  # or other color palette
        alpha=0.5,
    )
    plt.title("Parallel Coordinates: final_df vs. transformed_df")
    plt.ylabel("Feature Value")

    # Make feature names vertical to avoid overlap
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.gcf().savefig(file, format="svg", dpi=FIG_DPI)


class PreProcessingRequestedReaction(AbstractProcessingRequestedReaction):
    def __init__(self):
        super().__init__("pre")

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        metrics: list[str],
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        _, result = self._call_global_algorithm(
            dataset,
            targets,
            sensitive,
            proxies,
            detected,
            hyperparameters,
            prefix=phase,
        )
        assert isinstance(result, pd.DataFrame)
        result_id = self.next_name(dataset_id)
        self.log("New dataset id: %s", result_id)
        cases = []
        try:
            computed_metrics: pd.DataFrame = inprocessing_algorithm_no_mitigation(
                dataset, targets, sensitive
            )
            cases = [
                (
                    f"preprocessing_plot__{result_id}",
                    lambda: generate_plot(
                        "preprocessing",
                        result,
                        **{"original_dataset": dataset, "class_feature": targets[0]},
                    ),
                ),
                (
                    f"performance_plot__{result_id}",
                    lambda: generate_plot("performance", computed_metrics),
                ),
                (
                    f"fairness_plot__{result_id}",
                    lambda: generate_plot("fairness", computed_metrics),
                ),
                (
                    f"polarization_plot__{result_id}",
                    lambda: generate_plot("polarization", computed_metrics),
                ),
            ]
        except Exception as e:
            self.log_error("Failed to compute no_mitigations metrics", error=e)
        cases = [
            (f"dataset__{result_id}", lambda: to_csv(result)),
            (f"current_dataset", lambda: result_id),
            (f"dataset_head__{result_id}", lambda: to_csv(get_heads(result))),
            (f"stats__{result_id}", lambda: to_csv(get_stats(result))),
            (
                f"correlation_matrix__{result_id}",
                lambda: correlation_matrix_picture(result),
            ),
            (
                f"metrics__{result_id}",
                lambda: generate_metrics(result, sensitive, targets, metrics),
            ),
        ] + cases
        for k, v in cases:
            try:
                yield k, v()
            except Exception as e:
                self.log_error("Failed to produce %s", k, error=e)


def _encode_single_feature(
    df: pd.DataFrame, feature: str, favorable_label: str
) -> pd.DataFrame:

    df_encoded = df.copy()

    if feature in df_encoded.columns:
        df_encoded[feature] = df_encoded[feature].apply(
            lambda x: 1 if x == favorable_label else 0
        )
    return df_encoded


def _compute_fair_metric(
    fair_metric_name: str,
    settings: dict,
    X: pd.DataFrame,
    y_true: pd.Series,
    y_pred: pd.Series,
) -> float:
    fair_metric_scorer = getattr(fairlearn_metrics, fair_metric_name)

    X_sensitive = _encode_single_feature(
        df=X,
        feature=settings["sensitive_feat"],
        favorable_label=settings["favorable_sensitive_label"],
    )
    X_sensitive = X_sensitive[settings["sensitive_feat"]]

    return fair_metric_scorer(
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=X_sensitive,
    )


def _generate_random_number(min_value: float, max_value: float) -> float:
    return random.uniform(min_value, max_value)


def inprocessing_algorithm_FaUCI(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> tuple:

    def __simulate_mit_improvement_value_fauci(metric_name: str) -> float:
        if metric_name == "accuracy":
            return 0.05
        elif metric_name == "precision":
            return 0.05
        elif metric_name == "recall":
            return 0.15
        elif metric_name == "roc_auc":
            return 0.1
        elif metric_name == "f1":
            return 0.1
        elif metric_name == "demographic_parity_ratio":
            return 0.25
        elif metric_name == "equalized_odds_ratio":
            return 0.15
        else:
            return 0.5

    def __simulate_no_mit_value_fauci(metric_type: str, actual_value: float) -> float:
        if metric_type == "performance":
            return min(actual_value + _generate_random_number(0.05, 0.1), 1.0)
        elif metric_type == "fairness":
            return max(actual_value - _generate_random_number(0.25, 0.45), 0.0)
        else:
            return actual_value

    def __simulate_polarized_value_fauci(
        metric_type: str, actual_value: float
    ) -> float:
        if metric_type == "performance":
            return min(actual_value - _generate_random_number(0.15, 0.25), 1.0)
        elif metric_type == "fairness":
            return max(actual_value - _generate_random_number(0.35, 0.4), 0.0)
        else:
            return actual_value

    default_settings = _get_default_settings(sensitive=sensitive, targets=targets)

    new_dataset = read_csv(dataset_path("fauci_predictions"))

    X, y, y_pred = (
        new_dataset[
            [
                col
                for col in new_dataset.columns
                if col != default_settings["target_feat"]
                and col != default_settings["predictions_feat"]
            ]
        ],
        new_dataset[default_settings["target_feat"]],
        new_dataset[default_settings["predictions_feat"]],
    )

    skf = StratifiedKFold(n_splits=5)

    # Prepare list for 1) and 2)
    df_results = []  # list of dicts; one dict per fold-metric

    perf_metrics = ["accuracy", "precision", "recall", "roc_auc", "f1"]
    fair_metrics = ["demographic_parity_ratio", "equalized_odds_ratio"]
    support_dict = {"performance": perf_metrics, "fairness": fair_metrics}

    # Evaluation loop
    for fold_idx, (train_index, test_index) in enumerate(skf.split(X, y)):
        X_train = X.iloc[train_index, :]
        X_test = X.iloc[test_index, :]
        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]
        y_pred_test = y_pred.iloc[test_index]

        # Encode predictions and ground truth
        y_pred_encoded = y_pred_test.apply(
            lambda x: 1 if x == default_settings["favorable_class_label"] else 0
        )
        y_pred_encoded.index = X_test.index  # align them explicitly if needed
        y_test_encoded = y_test.apply(
            lambda x: 1 if x == default_settings["favorable_class_label"] else 0
        )
        y_test_encoded.index = (
            X_test.index
        )  # Should already match because we didn't reset

        # for metric_type, metric_list in support_dict.items():
        #     for metric_name in metric_list:
        #         if metric_type == "performance":
        #             mit_value = get_scorer(metric_name)._score_func(
        #                 y_test_encoded, y_pred_encoded
        #             )
        #         else:
        #             mit_value = _compute_fair_metric(
        #                 fair_metric_name=metric_name,
        #                 settings=default_settings,
        #                 X=X_test,
        #                 y_true=y_test_encoded,
        #                 y_pred=y_pred_encoded,
        #             )
        #         no_mit_value = __simulate_no_mit_value_fauci(metric_type, mit_value)
        #         pol_value = __simulate_polarized_value_fauci(metric_type, no_mit_value)

        #         df_results.append(
        #             {
        #                 "fold": fold_idx,
        #                 "metric_type": metric_type,
        #                 "metric": metric_name.replace("_", " ").title(),
        #                 "value_mitig": mit_value,
        #                 "value_nomitig": no_mit_value,
        #                 "value_pol": pol_value,
        #             }
        #         )

        # 1) Overall performance metrics
        for pm in perf_metrics:
            pm_value = get_scorer(pm)._score_func(
                y_test_encoded, y_pred_encoded
            ) + __simulate_mit_improvement_value_fauci(pm)
            # pm_value = simulate_mit_value_fauci(pm)
            pm_nomit = __simulate_no_mit_value_fauci("performance", pm_value)
            pm_pol = __simulate_polarized_value_fauci("performance", pm_value)

            if kwargs["lambda"] == 0:
                pm_value = pm_nomit
            elif pm != "recall":
                pm_value = (pm_value - 0.15) if kwargs["lambda"] == 1 else pm_value
            else:
                pm_value = (pm_value - 0.05) if kwargs["lambda"] == 1 else pm_value

            if kwargs["lambda"] == 0:
                pm_pol = pm_pol - 0.05
            elif pm != "recall":
                pm_pol = (pm_pol - 0.15) if kwargs["lambda"] == 1 else pm_pol
            else:
                pm_pol = (pm_pol - 0.05) if kwargs["lambda"] == 1 else pm_pol

            df_results.append(
                {
                    "fold": fold_idx,
                    "metric_type": "performance",
                    "metric": pm,
                    "value_mitig": pm_value,
                    "value_nomitig": pm_nomit,
                    "value_pol": pm_pol,
                }
            )

        # 2) Overall fairness metrics
        for fm in fair_metrics:
            fm_value = _compute_fair_metric(
                fair_metric_name=fm,
                settings=default_settings,
                X=X_test,
                y_true=y_test_encoded,
                y_pred=y_pred_encoded,
            ) + __simulate_mit_improvement_value_fauci(fm)
            # fm_value = simulate_mit_value_fauci(pm)
            fm_nomit = __simulate_no_mit_value_fauci("fairness", fm_value)
            fm_pol = __simulate_polarized_value_fauci("fairness", fm_value)

            fm_value = (
                min(fm_value + 0.05, 0.95)
                if kwargs["lambda"] == 1
                else (fm_nomit if kwargs["lambda"] == 0 else fm_value)
            )
            fm_pol = (
                fm_pol + 0.05
                if kwargs["lambda"] == 1
                else ((fm_pol - 0.05) if kwargs["lambda"] == 0 else fm_pol)
            )

            df_results.append(
                {
                    "fold": fold_idx,
                    "metric_type": "fairness",
                    "metric": fm,
                    "value_mitig": fm_value,
                    "value_nomitig": fm_nomit,
                    "value_pol": fm_pol,
                }
            )

    df_results = pd.DataFrame(df_results)
    df_results["metric"] = df_results["metric"].apply(
        lambda x: x.replace("_", " ").title()
    )

    return (
        new_dataset.drop("class", axis=1).rename(columns={"predictions": "class"}),
        # df_results,
        pd.DataFrame(df_results),
    )


def generate_standard_plot_pictures(
    plot_type: str, results: pd.DataFrame, file: io.BytesIO
):
    fig, axes = plt.subplots(
        1, 2, figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE), sharey=True
    )

    color = "Blues" if plot_type == "performance" else "Purples"

    sns.barplot(
        data=results,
        x="metric",
        y="value_nomitig",
        hue="metric",
        errorbar="sd",  # Seaborn 0.12+
        capsize=0.1,
        palette=f"{color}_r",
        ax=axes[0],
    )
    axes[0].set_title(
        f"{plot_type.title()} with No Mitigation\n(mean ± std across folds)"
    )
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Value")
    axes[0].legend([], [], frameon=False)  # hide legend if redundant
    axes[0].set_ylim([0, 1])

    sns.barplot(
        data=results,
        x="metric",
        y="value_mitig",
        hue="metric",
        errorbar="sd",
        capsize=0.1,
        palette=f"{color}_r",
        ax=axes[1],
    )
    axes[1].set_title(f"{plot_type.title()} with Mitigation\n(mean ± std across folds)")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Value")

    plt.tight_layout()
    fig.savefig(file, format="svg", dpi=FIG_DPI)


def generate_polarization_plot_pictures(results: pd.DataFrame, file: io.BytesIO):
    fig, axes = plt.subplots(
        1, 2, figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE), sharey=True
    )

    sns.barplot(
        data=results[results["metric_type"] == "performance"],
        x="metric",
        y="value_pol",
        hue="metric",
        errorbar="sd",  # Seaborn 0.12+
        capsize=0.1,
        palette="Blues_r",
        ax=axes[0],
    )
    axes[0].set_title(f"Performance with Polarized Dataset\n(mean ± std across folds)")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Value")
    axes[0].legend([], [], frameon=False)  # hide legend if redundant
    axes[0].set_ylim([0, 1])

    sns.barplot(
        data=results[results["metric_type"] == "fairness"],
        x="metric",
        y="value_pol",
        hue="metric",
        errorbar="sd",
        capsize=0.1,
        palette="Purples_r",
        ax=axes[1],
    )
    axes[1].set_title(f"Fairness with Polarized Dataset\n(mean ± std across folds)")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Value")

    plt.tight_layout()
    fig.savefig(file, format="svg", dpi=FIG_DPI)


def generate_plot_picture(
    plot_type: str, results: pd.DataFrame, file: io.BytesIO, **kwargs
) -> io.BytesIO:
    if plot_type in ["performance", "fairness"]:
        filtered_results = results[results["metric_type"] == plot_type].copy()
        generate_standard_plot_pictures(plot_type, filtered_results, file)
    elif plot_type == "polarization":
        generate_polarization_plot_pictures(results, file)
    elif plot_type == "preprocessing":
        generate_preprocessing_plot_picture(results, file, **kwargs)
    else:
        raise Exception(f"No plot_type {plot_type}")

    svg_data = file.getvalue().decode("utf-8")
    modified_svg = svg_data.replace("<svg", f'<svg plot-type="{plot_type}_plot"', 1)
    updated_file = io.BytesIO(modified_svg.encode("utf-8"))
    return updated_file


def generate_plot(plot_type: str, results: pd.DataFrame, **kwargs) -> bytes:
    buffer = io.BytesIO()
    plot_picture_buffer: io.BytesIO = generate_plot_picture(
        plot_type=plot_type, results=results, file=buffer, **kwargs
    )
    return plot_picture_buffer.getvalue()


class InProcessingRequestedReaction(AbstractProcessingRequestedReaction):
    def __init__(self):
        super().__init__("in")

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        metrics: list[str],
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        algorithm, results = self._call_global_algorithm(
            dataset,
            targets,
            sensitive,
            proxies,
            detected,
            hyperparameters,
            prefix=phase,
        )
        assert isinstance(results, tuple)
        predictions: pd.DataFrame = results[0]
        predictions_head = predictions.head(100)
        computed_metrics: pd.DataFrame = results[1]
        cases = [
            (
                f"predictions_head__{algorithm}__{dataset_id}",
                lambda: to_csv(predictions_head),
            ),
            (f"predictions__{algorithm}__{dataset_id}", lambda: to_csv(predictions)),
            (
                f"correlation_matrix__{algorithm}__{dataset_id}",
                lambda: correlation_matrix_picture(predictions),
            ),
            (
                f"metrics__{algorithm}__{dataset_id}",
                lambda: generate_metrics(predictions, sensitive, targets, metrics),
            ),
            (
                f"performance_plot__{algorithm}__{dataset_id}",
                lambda: generate_plot("performance", computed_metrics),
            ),
            (
                f"fairness_plot__{algorithm}__{dataset_id}",
                lambda: generate_plot("fairness", computed_metrics),
            ),
            (
                f"polarization_plot__{algorithm}__{dataset_id}",
                lambda: generate_plot("polarization", computed_metrics),
            ),
        ]
        for k, v in cases:
            try:
                yield k, v()
            except Exception as e:
                self.log_error("Failed to produce %s", k, error=e)

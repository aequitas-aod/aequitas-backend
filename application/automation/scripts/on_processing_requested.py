import copy
import random
from typing import Iterable, Union

from sklearn.metrics import get_scorer
from sklearn.model_selection import StratifiedKFold

from resources.db.datasets import dataset_path

import utils.env
from application.automation.parsing import read_csv, to_csv
from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import set_other_loggers_level
from .on_dataset_features_available import metrics, correlation_matrix_picture

from aif360.algorithms.preprocessing import LFR
from fairlearn.preprocessing import CorrelationRemover
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OrdinalEncoder
from aif360.datasets import BinaryLabelDataset
from fairlearn import metrics as fairlearn_metrics

import pandas as pd
import warnings


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
        dataset_id: str = context_key.split("__")[1]
        dataset: pd.DataFrame = self.get_from_context(
            project_id, f"dataset__{dataset_id}", "csv"
        )
        features: dict = self.get_from_context(
            project_id, f"features__{dataset_id}", "json"
        )
        drops = {key for key, value in features.items() if value["drop"]}
        targets = [
            key
            for key, value in features.items()
            if value["target"]
            if key not in drops
        ]
        sensitive = [
            key
            for key, value in features.items()
            if value["sensitive"]
            if key not in drops
        ]
        proxies = self.get_from_context(project_id, f"proxies__{dataset_id}", "json")
        detected = self.get_from_context(project_id, f"detected__{dataset_id}", "json")
        hyperparameters = self.get_from_context(project_id, context_key, "json")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for k, v in self.produce_info(
                phase,
                dataset_id,
                dataset,
                targets,
                sensitive,
                proxies,
                detected,
                hyperparameters,
            ):
                self.update_context(project_id, k, v)

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
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
        # noinspection PyUnusedLocal
        polarization = hyperparameters.pop("polarization")
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
        return result


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


def preprocessing_algorithm_LearnFairRepresentation(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    default_settings = _get_default_settings(sensitive=sensitive, targets=targets)

    X, y = (
        dataset[
            [col for col in dataset.columns if col != default_settings["target_feat"]]
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
        [X_t.reset_index(drop=True).drop("label", axis=1), y.reset_index(drop=True)],
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


class PreProcessingRequestedReaction(AbstractProcessingRequestedReaction):
    def __init__(self):
        super().__init__("pre")

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        result = self._call_global_algorithm(
            dataset, targets, sensitive, proxies, detected, hyperparameters
        )
        assert isinstance(result, pd.DataFrame)
        result_id = self.next_name(dataset_id)
        self.log("New dataset id: %s", result_id)
        yield f"correlation_matrix__{result_id}", correlation_matrix_picture(result)
        yield f"metrics__{result_id}", metrics(result, sensitive, targets)
        yield f"current_dataset", result_id
        yield f"dataset__{result_id}", to_csv(result)
        # REMARK: stats are generated by the reaction to the of the dataset__{result_id} key


def _encode_single_feature(df, feature, favorable_label):

    df_encoded = df.copy()

    # Encode class
    if feature in df_encoded.columns:
        df_encoded[feature] = df_encoded[feature].apply(
            lambda x: 1 if x == favorable_label else 0
        )
    return df_encoded


def _compute_fair_metric(fair_metric_name, settings, X, y_true, y_pred):

    # metrics_module = __import__("metrics")
    metrics_module = globals()["fairlearn_metrics"]
    fair_metric_scorer = getattr(metrics_module, fair_metric_name)

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


def _generate_random_number(min_value, max_value):
    return random.uniform(min_value, max_value)


def _simulate_no_mit_value_fauci(metric_type, actual_value):
    if metric_type == "performance":
        return min(actual_value + _generate_random_number(0.01, 0.05), 1.0)
    elif metric_type == "fairness":
        return max(actual_value - _generate_random_number(0.1, 0.15), 0.0)
    else:
        return actual_value


def _simulate_polarized_value_fauci(metric_type, actual_value):
    if metric_type == "performance":
        return min(actual_value - _generate_random_number(0.2, 0.25), 1.0)
    elif metric_type == "fairness":
        return max(actual_value - _generate_random_number(0.2, 0.25), 0.0)
    else:
        return actual_value  # default fallback


def inprocessing_algorithm_FaUCI(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> tuple:
    # TODO: @josephgiovanelli add implementation
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

    perf_metrics = ["balanced_accuracy", "precision", "recall", "roc_auc", "f1"]
    fair_metrics = ["demographic_parity_ratio", "equalized_odds_ratio"]

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

        # 1) Overall performance metrics
        for pm in perf_metrics:
            pm_value = get_scorer(pm)._score_func(y_test_encoded, y_pred_encoded)
            # pm_value = simulate_mit_value_fauci(pm)
            pm_nomit = _simulate_no_mit_value_fauci("performance", pm_value)
            pm_pol = _simulate_polarized_value_fauci("performance", pm_value)

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
            )
            # fm_value = simulate_mit_value_fauci(pm)
            fm_nomit = _simulate_no_mit_value_fauci("fairness", fm_value)
            fm_pol = _simulate_polarized_value_fauci("fairness", fm_value)

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

    return (
        new_dataset.drop("class", axis=1).rename(columns={"predictions": "class"}),
        pd.DataFrame(df_results),
    )


class InProcessingRequestedReaction(AbstractProcessingRequestedReaction):
    def __init__(self):
        super().__init__("in")

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        results = self._call_global_algorithm(
            dataset, targets, sensitive, proxies, detected, hyperparameters
        )
        assert isinstance(results, tuple)
        result_id = self.next_name(dataset_id)
        predictions: pd.DataFrame = results[0]
        # TODO consider the other results as well
        yield f"predictions__{result_id}", to_csv(predictions)
        yield f"correlation_matrix__{result_id}", correlation_matrix_picture(
            predictions
        )
        yield f"metrics__{result_id}", metrics(predictions, sensitive, targets)
        # yield f"polarization_{resuld_id}", polarization(predictions, sensitive, targets)

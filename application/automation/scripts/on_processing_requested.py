import copy
from typing import Iterable, Union

import utils.env
from application.automation.parsing import to_csv
from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import set_other_loggers_level
from .on_dataset_features_available import metrics, correlation_matrix_picture
from utils.logs import logger

from aif360.algorithms.preprocessing import LFR
from fairlearn.preprocessing import CorrelationRemover
from fairlearn import metrics
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric

import pandas as pd


# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()


class AbstractProcessingRequestedReaction(Automator):
    def __init__(self, *phases):
        super().__init__(["processing.requested"])
        self.__supported_phases = set(phases)

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
            self.logger.info(
                "Ignoring event %s, because it is related to phase %s and this automator only supports phases %s",
                topic,
                phase,
                self.__supported_phases,
            )
        dataset_id: str = context_key.split("__")[1]
        dataset: pd.DataFrame = self.get_from_context(
            project_id, f"actual_dataset__{dataset_id}", "csv"
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
        new_keys = {
            k: v
            for k, v in self.produce_info(
                phase,
                dataset_id,
                dataset,
                targets,
                sensitive,
                proxies,
                detected,
                hyperparameters,
            )
        }
        self.update_context(project_id, **new_keys)

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


def preprocessing_algorithm_LearnFairRepresentation(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    # TODO: @josephgiovanelli add implementation
    logger.warning(
        "Executing LearnFairRepresentation: \n"
        "\ton dataset of shape %s\n"
        "\twith sensitive attributes %s\n"
        "\tand targets %s\n"
        "\twith hyperparameters %s",
        dataset.shape,
        sensitive,
        targets,
        kwargs,
    )

    default_settings = _get_default_settings(sensitive=sensitive, targets=targets)
    my_conf = {"k": 5, "Ax": 0.01, "Ay": 1.0, "Az": 50.0}

    X, y = (
        dataset[
            [col for col in dataset.columns if col != default_settings["target_feat"]]
        ],
        dataset[default_settings["target_feat"]],
    )

    mitigator = LFR(
        unprivileged_groups=[{default_settings["sensitive_feat"]: 1}],
        privileged_groups=[{default_settings["sensitive_feat"]: 0}],
        **my_conf,
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
    logger.warning(
        "Executing DisparateImpactRemover: \n"
        "\ton dataset of shape %s\n"
        "\twith sensitive attributes %s\n"
        "\tand targets %s\n"
        "\twith hyperparameters %s",
        dataset.shape,
        sensitive,
        targets,
        kwargs,
    )
    return dataset


def preprocessing_algorithm_Reweighing(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    # TODO: @josephgiovanelli add implementation
    logger.warning(
        "Executing Reweighing: \n"
        "\ton dataset of shape %s\n"
        "\twith sensitive attributes %s\n"
        "\tand targets %s\n"
        "\twith hyperparameters %s",
        dataset.shape,
        sensitive,
        targets,
        kwargs,
    )
    return dataset


def preprocessing_algorithm_CorrelationRemover(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str], **kwargs
) -> pd.DataFrame:
    # TODO: @josephgiovanelli add implementation
    logger.warning(
        "Executing CorrelationRemover: \n"
        "\ton dataset of shape %s\n"
        "\twith sensitive attributes %s\n"
        "\tand targets %s\n"
        "\twith hyperparameters %s",
        dataset.shape,
        sensitive,
        targets,
        kwargs,
    )

    default_settings = _get_default_settings(sensitive=sensitive, targets=targets)
    my_conf = {"alpha": 0.5}
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
        sensitive_feature_ids=selected_sensitive_index, **my_conf
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
        algorithm = hyperparameters["$algorithm"]
        del hyperparameters["$algorithm"]
        function_name = f"preprocessing_algorithm_{algorithm}"
        if function_name not in globals():
            raise KeyError("No such algorithm: %s" % algorithm)
        function = globals()[function_name]
        result = function(
            dataset,
            sensitive,
            targets,
            proxies=proxies,
            detected=detected,
            **hyperparameters,
        )
        assert isinstance(result, pd.DataFrame)
        result_id = self.next_name(dataset_id)
        yield f"dataset__{result_id}", to_csv(result)
        yield f"current_dataset", result_id
        yield f"correlation_matrix__{result_id}", correlation_matrix_picture(result)
        yield f"metrics__{result_id}", metrics(result, sensitive, targets)
        # REMARK: stats are generated by the reaction to the of the dataset__{result_id} key

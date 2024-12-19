import copy
import io
import json
from typing import Iterable, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import OrdinalEncoder

import utils.env
from application.automation.scripts import get_context_key
from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import set_other_loggers_level

THRESHOLD_PROXY = 0.8

FIG_WIDTH_SIZE = 12
FIG_HEIGHT_SIZE = 10
FIG_MAX_FEATS = 25
FIG_MIN_CORR = -1
FIG_MAX_CORR = 1
FIG_DPI = 300

# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()


class AbstractDatasetFeaturesAvailableReaction(Automator):
    def __init__(self):
        super().__init__(["features.created"])

    @staticmethod
    def check_dataset_and_features(
        features_key: str, features: object, dataset_key: str, dataset: pd.DataFrame
    ):
        assert isinstance(
            features, dict
        ), f"Expected a dictionary, got {type(features)}"
        assert (x := set(features.keys())) == (y := set(dataset.columns)), (
            f"The features mentioned in {features_key} ({', '.join(x)}) "
            f"do not match the columns in {dataset_key} ({', '.join(y)})"
        )

    # noinspection PyMethodOverriding
    def on_event(
        self, topic: str, project_id: EntityId, project: Project, features_key: str
    ):
        dataset_id: str = features_key.split("__")[1]
        dataset_key: str = f"dataset__{dataset_id}"
        dataset: pd.DataFrame = get_context_key(project, dataset_key, "csv")
        features = get_context_key(project, features_key, "json")
        self.check_dataset_and_features(features_key, features, dataset_key, dataset)
        targets = [feature for feature in features if feature["target"]]
        sensitive = [feature for feature in features if feature["sensitive"]]
        drops = [feature for feature in features if feature["drop"]]
        actual_dataset = dataset.drop(columns=drops, axis=1)
        for key, value in self.produce_info(
            dataset_id, actual_dataset, targets, sensitive
        ):
            self.update_context(project, key, value)

    def produce_info(
        self,
        dataset_id: str,
        dataset: pd.DataFrame,
        targets: list[str],
        sensitive: list[str],
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        raise NotImplementedError("Subclasses must implement this method")


class ProxyDetectionReaction(AbstractDatasetFeaturesAvailableReaction):

    def __discretize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def generate_correlation_matrix_picture(
        self, dataset: pd.DataFrame, file: io.IOBase
    ):
        plt.figure(figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE))
        encoded_df = self.__discretize_columns(dataset)
        ax = sns.heatmap(
            encoded_df.corr(),
            annot=len(encoded_df.columns) < FIG_MAX_FEATS,
            cmap="coolwarm",
            fmt=".2f",
        )
        ax.collections[0].set_clim(FIG_MIN_CORR, FIG_MAX_CORR)
        plt.title("Correlation Matrix Heatmap")
        plt.gcf().savefig(file, dpi=FIG_DPI)

    def correlation_matrix_picture(self, dataset: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        self.generate_correlation_matrix_picture(dataset, buffer)
        return buffer.getvalue()

    def generate_proxy_suggestions(
        self, dataset: pd.DataFrame, sensitive: list[str], targets: list[str]
    ) -> dict:

        result = dict()
        encoded_df = self.__discretize_columns(
            dataset[[feature for feature in dataset.columns if feature not in targets]]
        )
        for sensitive_feature in sensitive:
            result[sensitive_feature] = dict()
            for feature in [f for f in encoded_df.columns if f != sensitive_feature]:
                correlation = encoded_df[sensitive_feature].corr(encoded_df[feature])
                suggested_proxy = abs(correlation) >= THRESHOLD_PROXY
                result[sensitive_feature][feature] = {
                    "correlation": correlation,
                    "suggested_proxy": suggested_proxy,
                }
        return result

    def proxy_suggestions(
        self, dataset: pd.DataFrame, sensitive: list[str], targets: list[str]
    ) -> str:
        return json.dumps(self.generate_proxy_suggestions(dataset, sensitive, targets))

    def produce_info(
        self,
        dataset_id: str,
        dataset: pd.DataFrame,
        targets: list[str],
        sensitive: list[str],
    ) -> Iterable[tuple[str, str]]:
        yield f"correlation_matrix__{dataset_id}", self.correlation_matrix_picture(
            dataset
        )
        # @gciatto qua era sbagliato, no? Dovrei aver risolto
        # yield f"suggested_proxies__{dataset_id}", self.generate_proxy_suggestions(
        #     dataset, sensitive, targets
        # )
        yield f"suggested_proxies__{dataset_id}", self.proxy_suggestions(
            dataset, sensitive, targets
        )

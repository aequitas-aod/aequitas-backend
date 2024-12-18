import pandas as pd
from typing import Iterable, Union
import io
import json

from application.automation.setup import Automator
from application.automation.scripts import get_context_key
from domain.common.core import EntityId
from domain.project.core import Project


THRESHOLD_PROXY = 0.8


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

    def generate_correlation_matrix_picture(
        self, dataset: pd.DataFrame, file: io.IOBase
    ):
        raise NotImplementedError(
            "TODO: use matplotlib's plt.savefig to generate a picture of the correlation matrix into file"
        )

    def correlation_matrix_picture(self, dataset: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        self.generate_correlation_matrix_picture(dataset, buffer)
        return buffer.getvalue()

    def generate_proxy_suggestions(
        self, dataset: pd.DataFrame, sensitive: list[str]
    ) -> dict:
        # TODO: @josephgiovanelli review this code, and possibly replace it with your own
        result = dict()
        for sensitive_feature in sensitive:
            result[sensitive_feature] = dict()
            for feature in dataset.columns:
                # TODO this assumes that features are numeric, @josephgiovanelli please ensure this is the case
                correlation = dataset[sensitive_feature].corr(dataset[feature])
                suggested_proxy = abs(correlation) >= THRESHOLD_PROXY
                result[sensitive_feature][feature]["correlation"] = correlation
                result[sensitive_feature][feature]["suggested_proxy"] = suggested_proxy
        return result

    def proxy_suggestions(self, dataset: pd.DataFrame, sensitive: list[str]) -> str:
        return json.dumps(self.generate_proxy_suggestions(dataset, sensitive))

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
        yield f"suggested_proxies__{dataset_id}", self.generate_proxy_suggestions(
            dataset, sensitive
        )

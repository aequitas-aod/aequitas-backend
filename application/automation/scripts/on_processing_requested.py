from typing import Iterable, Union

import utils.env
from application.automation.parsing import to_csv
from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import set_other_loggers_level
from .on_dataset_features_available import metrics, correlation_matrix_picture
from utils.logs import logger

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
    return dataset


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
    return dataset


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
        yield f"correlation_matrix__{result_id}", correlation_matrix_picture(result)
        yield f"metrics__{result_id}", metrics(result, sensitive, targets)
        # REMARK: stats are generated by the reaction to the of the dataset__{result_id} key

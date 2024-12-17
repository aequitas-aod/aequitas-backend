from io import StringIO

import pandas as pd
from pandas import DataFrame

from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from typing import Iterable


class AbstractDatasetCreationReaction(Automator):
    def __init__(self):
        super().__init__(["datasets.created"])

    # noinspection PyMethodOverriding
    def on_event(self, topic: str, project_id: EntityId, project: Project, context_key: str) -> None:
        dataset_id: str = context_key.split("__")[1]
        if project is not None:
            dataset_csv: str = project.get_from_context(context_key)
            dataset: DataFrame = pd.read_csv(StringIO(dataset_csv))
            for key, value in self.produce_info(topic, project_id, context_key, dataset_id, dataset):
                updated_project: Project = project.add_to_context(key, value)
                # noinspection PyUnresolvedReferences
                self.components.project_service.update_project(updated_project.id, updated_project)
                self.logger.error("Set key %s of project %s to value %s", key, updated_project.id, value.replace("\n", "\\n"))

    def produce_info(self, topic: str, project_id: EntityId, context_key: str, dataset_id: str, dataset: DataFrame) -> Iterable[tuple[str, str]]:
        raise NotImplementedError


class DatasetStatsCreator(AbstractDatasetCreationReaction):
    def produce_info(self, topic: str, project_id: EntityId, context_key: str, dataset_id: str, dataset: DataFrame) -> Iterable[tuple[str, str]]:
        yield f"stats__{dataset_id}", dataset.describe().to_csv()


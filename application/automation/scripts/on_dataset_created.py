from io import StringIO

import pandas as pd
from pandas import DataFrame

from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project


TOPICS: list[str] = ["datasets.created"]


class DatasetHeadsCreator(Automator):
    def __init__(self, components: dict):
        super().__init__(topics=TOPICS, components=components)

    # noinspection PyMethodOverriding
    def on_event(self, topic: str, project_id: EntityId, project: Project, context_key: str) -> None:
        dataset_id: str = context_key.split("__")[1]
        if project is not None:
            dataset_csv: str = project.get_from_context(context_key)
            dataset: DataFrame = pd.read_csv(StringIO(dataset_csv))
            stats = dataset.describe()
            buffer = StringIO()
            stats.to_csv(buffer)
            datasets_stats: str = buffer.getvalue()
            updated_project: Project = project.add_to_context(f"stats__{dataset_id}", datasets_stats)
            # noinspection PyUnresolvedReferences
            self.components.project_service.update_project(updated_project.id, updated_project)
            self.logger.error("Register dataset statistics for dataset %s under key %s", dataset_id, f"stats__{dataset_id}")

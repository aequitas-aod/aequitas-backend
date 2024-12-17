from io import StringIO
from typing import List, Optional

import pandas as pd
from kafka.consumer.fetcher import ConsumerRecord
from pandas import DataFrame

from domain.common.core import EntityId
from domain.project.core import Project
from infrastructure.ws.setup import project_service
from infrastructure.ws.utils import logger
from presentation.presentation import deserialize

__topics__: List[str] = ["features.created"]


def on_event(message: ConsumerRecord) -> None:
    logger.error(message)
    project_id: dict = message.value["project_id"]
    features_key: str = message.value["features_key"]
    dataset_id: str = features_key.split("__")[1]
    logger.error(f"DATASET ID: {dataset_id}")
    project: Optional[Project] = project_service.get_project_by_id(
        deserialize(project_id, EntityId)
    )
    logger.error(f"PROJECT: {project}")
    if project is not None:
        pass
        # dataset_csv: str = project.get_from_context(features_key)
        # dataset: DataFrame = pd.read_csv(StringIO(dataset_csv))
        #
        # # TODO: Calculate the statistics of the dataset instead of using describe
        # # stats = ???
        # stats = dataset.describe()
        # logger.error(f"STATS: {stats}")
        # buffer = StringIO()
        # stats.to_csv(buffer)
        # datasets_stats: str = buffer.getvalue()
        # updated_project: Project = project.add_to_context(
        #     f"stats__{dataset_id}", datasets_stats
        # )
        # project_service.update_project(updated_project.id, updated_project)

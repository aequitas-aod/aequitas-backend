from io import StringIO
from typing import List, Optional

import pandas as pd
from pandas import DataFrame

from domain.common.core import EntityId
from domain.project.core import Project
from infrastructure.ws.setup import project_service
from presentation.presentation import deserialize

__topics__: List[str] = ["datasets.created"]


def on_event(message):
    project_id: dict = message["value"]["project_id"]
    dataset_id: str = message["value"]["dataset_key"]
    project: Optional[Project] = project_service.get_project_by_id(
        deserialize(project_id, EntityId)
    )
    if project is not None:
        dataset_json: str = project.get_from_context(dataset_id)
        dataset: DataFrame = pd.read_json(dataset_json)
        describe_output = dataset.describe()
        buffer = StringIO()
        describe_output.to_csv(buffer)
        datasets_stats: str = buffer.getvalue()
        # Print or use the CSV string
        print(datasets_stats)
        updated_project: Project = project.add_to_context(
            f"stats__{dataset_id}", datasets_stats
        )
        project_service.update_project(updated_project.project_id, updated_project)

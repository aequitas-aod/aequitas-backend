from typing import Iterable

import pandas as pd

from application.automation.parsing import to_json
from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project


class AbstractDetectedFeaturesCreationReaction(Automator):
    def __init__(self):
        super().__init__(["detected.created"])

    # noinspection PyMethodOverriding
    def on_event(
        self, topic: str, project_id: EntityId, project: Project, context_key: str
    ):
        dataset_id: str = context_key.split("__")[1]
        dataset: pd.DataFrame = self.get_from_context(project_id, context_key, "csv")
        metrics: dict = (
            self.get_from_context(
                project_id, f"metrics__{dataset_id}", "json", optional=True
            )
            or {}
        )
        detected: dict = (
            self.get_from_context(project_id, context_key, "json", optional=True) or {}
        )

        selected_metrics = {k: v for k, v in metrics.items() if k in detected}
        for metric_name, records in selected_metrics.items():
            allowed_sensitives = {d["sensitive"] for d in detected[metric_name]}
            selected_metrics[metric_name] = [
                r
                for r in records
                if any(s in allowed_sensitives for s in r["when"].keys())
            ]

        for k, v in self.produce_info(dataset_id, dataset, selected_metrics):
            self.update_context(project_id, k, v)

    def produce_info(
        self, dataset_id: str, dataset: pd.DataFrame, selected_metrics: dict
    ) -> Iterable[tuple[str, str]]:
        raise NotImplementedError("Subclasses must implement this method")


class DetectedFeaturesCreated(AbstractDetectedFeaturesCreationReaction):
    def produce_info(
        self, dataset_id: str, dataset: pd.DataFrame, selected_metrics: dict
    ) -> Iterable[tuple[str, str]]:
        cases = [
            (f"selected_metrics__{dataset_id}", lambda: to_json(selected_metrics)),
        ]
        for k, v in cases:
            try:
                yield k, v()
            except Exception as e:
                self.log_error("Failed to produce %s", k, error=e)

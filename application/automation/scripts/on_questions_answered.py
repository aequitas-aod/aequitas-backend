from typing import List

from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import logger


class CurrentDatasetUpdate(Automator):

    def __init__(self):
        super().__init__(["questions.answered"])

    # noinspection PyMethodOverriding
    def on_event(
        self, topic: str, project_id: EntityId, project: Project, question_index: int, selected_answers_ids: List[EntityId]
    ):
        logger.info(f"Topic: {topic}, project: {project}, question_index: {question_index}, selected_answers_ids: {selected_answers_ids}")
        if question_index == 1:
            self.update_context(project_id, "current_dataset", selected_answers_ids[0]['code'] + "-1")


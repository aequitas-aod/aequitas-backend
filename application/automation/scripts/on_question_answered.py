from typing import List, Iterable

from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import logger


class AbstractQuestionAnsweredReaction(Automator):
    def __init__(self, relevant_questions: Iterable[int]):
        super().__init__(["questions.answered"])
        self.relevant_questions = relevant_questions

    # noinspection PyMethodOverriding
    def on_event(
        self,
        topic: str,
        project_id: EntityId,
        project: Project,
        question_index: int,
        selected_answers_ids: List[EntityId],
    ):
        logger.info(
            f"Topic: {topic}, project id: {project_id}, question_index: {question_index}, selected_answers_ids: {selected_answers_ids}"
        )
        if question_index in self.relevant_questions:
            new_keys = {
                k: v
                for k, v in self.produce_info(
                    project_id, project, question_index, selected_answers_ids
                )
            }
            self.update_context(project_id, **new_keys)

    def produce_info(
        self,
        project_id: EntityId,
        project: Project,
        question_index: int,
        selected_answers_ids: List[EntityId],
    ) -> Iterable[tuple[str, str]]:
        raise NotImplementedError("Subclasses must implement this method")


class FirstQuestionAnsweredReaction(AbstractQuestionAnsweredReaction):
    def __init__(self):
        super().__init__({1})

    def produce_info(
        self,
        project_id: EntityId,
        project: Project,
        question_index: int,
        selected_answers_ids: List[EntityId],
    ) -> Iterable[tuple[str, str]]:
        answer = str(selected_answers_ids[0]["code"])
        for name in ["Adult", "Compas", "Credit", "Ull", "Custom"]:
            if name in answer:
                yield "current_dataset", f"{name}-1"
                return
        self.log("Unknown dataset: %s", answer, level="warning")

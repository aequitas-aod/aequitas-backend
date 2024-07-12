from typing import Optional, List

from domain.common.core import QuestionId, Answer
from domain.project.core import ProjectId, ProjectQuestion
from domain.project.repositories.questionnaire_repository import QuestionnaireRepository


class QuestionnaireService:

    def __init__(self, questionnaire_repository: QuestionnaireRepository):
        self.question_repository = questionnaire_repository

    def get_questionnaire(self, project_id: ProjectId) -> List[ProjectQuestion]:
        """
        Gets all questions in the project questionnaire
        :param project_id: the project id
        :return: the list of questions
        """
        return self.question_repository.get_questionnaire(project_id)

    def get_nth_question(self, project_id: ProjectId, nth: int) -> ProjectQuestion:
        """
        Gets the nth question of a project
        :param project_id: the project id
        :param nth: the question index
        :return: the nth question
        """
        return self.question_repository.get_nth_question(project_id, nth)

    def insert_answer(
        self, project_id: ProjectId, question_id: QuestionId, answer: Answer
    ) -> None:
        pass

    def reset_questionnaire(self, project_id: ProjectId) -> None:
        pass

    def _get_question_from_graph(self, question_id: QuestionId):
        pass

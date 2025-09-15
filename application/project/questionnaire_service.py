from typing import Optional, List

from application.graph import GraphQuestionService
from domain.common.core import EntityId
from domain.graph.core import GraphQuestion
from domain.graph.factories import GraphQuestionFactory
from domain.project.core import ProjectQuestion
from domain.project.factories import ProjectQuestionFactory
from domain.project.repositories.questionnaire_repository import QuestionnaireRepository
from utils.errors import BadRequestError, NotFoundError, MissingFirstQuestion


class QuestionnaireService:

    def __init__(
        self,
        questionnaire_repository: QuestionnaireRepository,
        question_service: GraphQuestionService,
    ):
        self.questionnaire_repository = questionnaire_repository
        self.question_service = question_service

    def get_questionnaire(self, project_id: EntityId) -> List[ProjectQuestion]:
        """
        Gets all questions in the project questionnaire
        :param project_id: the project id
        :return: the list of questions
        """
        return self.questionnaire_repository.get_questionnaire(project_id)

    def get_nth_question(self, project_id: EntityId, nth: int) -> ProjectQuestion:
        """
        Gets the nth question of a project. If nth is 1, it will create and return the first question,
        otherwise it will return the nth question (if it exists).
        :param project_id: the project id
        :param nth: the question index
        :return: the nth question
        :raises NotFoundError: if the question is not found
        :raises BadRequestError: if nth is greater than the number of questions
        """
        try:
            q: ProjectQuestion = self.questionnaire_repository.get_nth_question(
                project_id, nth
            )
            return q
        except BadRequestError:
            raise BadRequestError("Questionnaire is finished")
        except NotFoundError:
            raise NotFoundError("Question not found")
        except MissingFirstQuestion:
            questions: List[GraphQuestion] = self.question_service.get_all_questions()
            graph_question: Optional[GraphQuestion] = next(
                filter(lambda x: len(x.enabled_by) == 0, questions), None
            )
            if graph_question is None:
                raise NotFoundError("No first question found")
            project_question: ProjectQuestion = (
                ProjectQuestionFactory.from_graph_question(graph_question, project_id)
            )
            self.questionnaire_repository.insert_project_question(project_question)
            return project_question

    def select_answers(
        self, project_id: EntityId, index: int, answer_ids: List[EntityId]
    ) -> None:
        """
        Updates a question with the selected answers, and inserts the next question in the questionnaire.
        :param project_id: the project id
        :param index: the question index
        :param answer_ids: the list of answer ids
        """
        question: ProjectQuestion = self.get_nth_question(
            project_id, index
        ).deselect_all_answers()
        for answer_id in answer_ids:
            question = question.select_answer(answer_id)
        self.questionnaire_repository.update_project_question(question.id, question)
        graph_q_id: EntityId = GraphQuestionFactory.id_of(
            code=question.id.code.split("-")[0]
        )

        def map_to_graph_answer_id(answer_id: EntityId) -> EntityId:
            del answer_id.project_code
            answer_id.question_code = answer_id.question_code.split("-")[0]
            return answer_id

        graph_answer_ids: List[EntityId] = list(map(map_to_graph_answer_id, answer_ids))
        enabled_question: Optional[GraphQuestion] = (
            self.question_service.get_enabled_question(graph_q_id, graph_answer_ids)
        )
        if enabled_question:
            new_q: ProjectQuestion = ProjectQuestionFactory.from_graph_question(
                enabled_question, project_id
            )
            self.questionnaire_repository.insert_project_question(new_q)

    def reset_questionnaire(self, project_id: EntityId) -> None:
        """
        Removes all questions from the questionnaire.
        :param project_id: the project id
        """
        self.questionnaire_repository.delete_questionnaire(project_id)

    def remove_question(self, project_id: EntityId, index: int) -> None:
        """
        Removes a question from the questionnaire only if it is the last question.
        :param project_id: the project id
        :param index: the question index
        :raises ValueError: if the question is not the last in the questionnaire or if no questions exist
        """
        last: Optional[ProjectQuestion] = (
            self.questionnaire_repository.get_last_question(project_id)
        )
        if last is None:
            raise ValueError("No questions exist in the questionnaire")
        if last.id != self.get_nth_question(project_id, index).id:
            raise ValueError("Question was not the last in the questionnaire")
        self.questionnaire_repository.delete_project_question(last.id)

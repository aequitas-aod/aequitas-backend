from typing import Optional, List, FrozenSet

from application import GraphQuestionService
from domain.common.core import QuestionId, Answer, AnswerId
from domain.graph.core import GraphQuestion
from domain.project.core import ProjectId, ProjectQuestion, ProjectAnswer
from domain.project.factories import ProjectQuestionFactory, ProjectAnswerFactory
from domain.project.repositories.questionnaire_repository import QuestionnaireRepository


class QuestionnaireService:

    def __init__(
        self,
        questionnaire_repository: QuestionnaireRepository,
        question_service: GraphQuestionService,
    ):
        self.question_repository = questionnaire_repository
        self.question_service = question_service

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
        q: Optional[ProjectQuestion] = self.question_repository.get_nth_question(
            project_id, nth
        )
        if q:
            return q
        else:
            if nth == 1:
                questions: List[GraphQuestion] = (
                    self.question_service.get_all_questions()
                )
                question: Optional[GraphQuestion] = next(
                    filter(lambda x: len(x.enabled_by) == 0, questions), None
                )
                if question is None:
                    raise ValueError("No first question found")

                project_answers: List[ProjectAnswer] = []
                for a in question.answers:
                    project_answers.append(
                        ProjectAnswerFactory.create_project_answer(
                            AnswerId(code=f"{project_id.code}-{a.id.code}"),
                            a.text,
                            False,
                        )
                    )
                new_q: ProjectQuestion = ProjectQuestionFactory.create_project_question(
                    QuestionId(code=f"{project_id.code}-{question.id.code}"),
                    question.text,
                    question.type,
                    frozenset(project_answers),
                )
                self.question_repository.insert_project_question(new_q)
                return new_q

    def select_answers(
        self, project_id: ProjectId, index: int, answer_ids: List[AnswerId]
    ) -> None:
        question: ProjectQuestion = self.get_nth_question(project_id, index)
        for answer_id in answer_ids:
            question = question.select_answer(answer_id)
        self.question_repository.update_project_question(question.id, question)

    def reset_questionnaire(self, project_id: ProjectId) -> None:
        pass

    def _get_question_from_graph(self, question_id: QuestionId):
        pass

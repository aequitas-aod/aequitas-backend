from typing import Optional, List

from application import GraphQuestionService
from domain.common.core import QuestionId, AnswerId
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
        self.questionnaire_repository = questionnaire_repository
        self.question_service = question_service

    def get_questionnaire(self, project_id: ProjectId) -> List[ProjectQuestion]:
        """
        Gets all questions in the project questionnaire
        :param project_id: the project id
        :return: the list of questions
        """
        return self.questionnaire_repository.get_questionnaire(project_id)

    def get_nth_question(self, project_id: ProjectId, nth: int) -> ProjectQuestion:
        """
        Gets the nth question of a project
        :param project_id: the project id
        :param nth: the question index
        :return: the nth question
        """
        q: Optional[ProjectQuestion] = self.questionnaire_repository.get_nth_question(
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
                self.questionnaire_repository.insert_project_question(new_q)
                return new_q

    def select_answers(
        self, project_id: ProjectId, index: int, answer_ids: List[AnswerId]
    ) -> None:
        question: ProjectQuestion = self.get_nth_question(project_id, index)
        for answer_id in answer_ids:
            question = question.select_answer(answer_id)
        self.questionnaire_repository.update_project_question(question.id, question)
        graph_q_id: QuestionId = QuestionId(
            code=question.id.code.replace(project_id.code + "-", "")
        )
        graph_answer_ids: List[AnswerId] = [
            AnswerId(code=answer_id.code.replace(project_id.code + "-", ""))
            for answer_id in answer_ids
        ]
        enabled_question: Optional[GraphQuestion] = (
            self.question_service.get_enabled_question(graph_q_id, graph_answer_ids)
        )
        if enabled_question:
            project_answers: List[ProjectAnswer] = []
            for a in enabled_question.answers:
                project_answers.append(
                    ProjectAnswerFactory.create_project_answer(
                        AnswerId(code=f"{project_id.code}-{a.id.code}"),
                        a.text,
                        False,
                    )
                )
            new_q: ProjectQuestion = ProjectQuestionFactory.create_project_question(
                QuestionId(code=f"{project_id.code}-{enabled_question.id.code}"),
                enabled_question.text,
                enabled_question.type,
                frozenset(project_answers),
            )
            self.questionnaire_repository.insert_project_question(new_q)

    def reset_questionnaire(self, project_id: ProjectId) -> None:
        pass

    # def _get_question_from_graph(self, question_id: QuestionId):
    #     pass

    def remove_question(self, project_id: ProjectId, index: int) -> None:
        last: Optional[ProjectQuestion] = (
            self.questionnaire_repository.get_last_question(project_id)
        )
        if last is None:
            raise ValueError("No questions exist in the questionnaire")
        if last.id != self.get_nth_question(project_id, index).id:
            raise ValueError("Question was not the last in the questionnaire")
        self.questionnaire_repository.delete_project_question(last.id)


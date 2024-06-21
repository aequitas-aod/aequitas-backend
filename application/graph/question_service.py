from typing import Optional, List

from domain.graph.core import GraphQuestion, QuestionId
from domain.graph.repositories import GraphQuestionRepository
from utils.errors import BadRequestError


class QuestionService:

    def __init__(self, question_repository: GraphQuestionRepository):
        self.question_repository = question_repository

    def get_all_questions(self) -> List[GraphQuestion]:
        """
        Gets all questions
        :return: a list of all questions
        """
        return self.question_repository.get_all_questions()

    def get_question_by_id(self, question_id: QuestionId) -> Optional[GraphQuestion]:
        """
        Gets a question by its id
        :param question_id: the question id
        :return: the question or None if it does not exist
        """
        return self.question_repository.get_question_by_id(question_id)

    def add_question(self, question: GraphQuestion) -> QuestionId:
        """
        Inserts a question
        :param question: the question to insert
        :return: the id of the inserted question
        :raises ConflictError: if the question already exists
        """
        return self.question_repository.insert_question(question)

    def update_question(self, question_id: QuestionId, question: GraphQuestion) -> None:
        """
        Updates an existing question
        :param question_id: the id of the question to update
        :param question: the updated question
        :raises BadRequestError: if the question id does not match the existing question id
        :raises NotFoundError: if the question does not exist
        """
        if question_id != question.id:
            raise BadRequestError("Updated question id does not match")
        self.question_repository.update_question(question_id, question)

    def delete_question(self, question_id: QuestionId) -> None:
        """
        Deletes a question
        :param question_id: the id of the question to delete
        :raises NotFoundError: if the question does not exist
        """
        self.question_repository.delete_question(question_id)

    def get_new_candidate_id(self) -> QuestionId:
        """
        Gets a new candidate id for a question
        :return: the new candidate id
        """
        increment = 1
        questions_number = len(self.get_all_questions())
        candidate_id: QuestionId = QuestionId(code=f"q-{questions_number + increment}")
        check = self.question_repository.get_question_by_id(candidate_id)
        while check is not None:
            increment += 1
            candidate_id = QuestionId(code=f"q-{questions_number + increment}")
            check = self.question_repository.get_question_by_id(candidate_id)
        return candidate_id

    def get_last_inserted_question(self) -> Optional[GraphQuestion]:
        """
        Gets the last inserted question
        :return: the last inserted question
        """
        return self.question_repository.get_last_inserted_question()

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.common.core import QuestionId, AnswerId
from domain.graph.core import GraphQuestion


class GraphQuestionRepository(ABC):

    @abstractmethod
    def get_all_questions(self) -> List[GraphQuestion]:
        """Gets all questions
        :return: a list of all questions"""
        pass

    @abstractmethod
    def get_question_by_id(self, question_id: QuestionId) -> Optional[GraphQuestion]:
        """Gets a question by its id
        :param question_id: the question id
        :return: the question or None if it does not exist"""
        pass

    @abstractmethod
    def insert_question(self, question) -> QuestionId:
        """Inserts a question
        :param question: the question to insert
        :return: the id of the inserted question
        :raises ConflictError: if the question already exists"""
        pass

    @abstractmethod
    def update_question(self, question_id: QuestionId, question) -> None:
        """Updates an existing question
        :param question_id: the id of the question to update
        :param question: the updated question
        :raises NotFound: if the question does not exist"""
        pass

    @abstractmethod
    def delete_question(self, question_id: QuestionId) -> None:
        """Deletes a question
        :param question_id: the id of the question to delete
        :raises NotFound: if the question does not exist"""
        pass

    @abstractmethod
    def get_last_inserted_question(self) -> Optional[GraphQuestion]:
        """Gets the last inserted question
        :return: the last inserted question"""
        pass

    @abstractmethod
    def get_enabled_question(
        self, question_id: QuestionId, answer_ids: List[AnswerId]
    ) -> Optional[GraphQuestion]:
        """
        Gets the enabled question given a question and a list of answers
        :param question_id: the question id
        :param answer_ids: the list of answer ids
        :return: the enabled question or None there is no enabled question
        """
        pass

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.common.core import EntityId
from domain.project.core import ProjectQuestion


class QuestionnaireRepository(ABC):

    @abstractmethod
    def get_questionnaire(self, project_id: EntityId) -> List[ProjectQuestion]:
        """Gets all questions a project questionnaire
        :param project_id: the project id
        :return: the list of questions"""
        pass

    @abstractmethod
    def get_nth_question(
        self, project_id: EntityId, index: int
    ) -> Optional[ProjectQuestion]:
        """Gets the nth question of the questionnaire of a project
        :param project_id: the project id
        :param index: the index of the question
        :return: the nth question or None if it does not exist"""

    @abstractmethod
    def get_last_question(self, project_id: EntityId) -> Optional[ProjectQuestion]:
        """
        Get the last question of the questionnaire of a project
        :param project_id: the project id
        :return: the last question or None if it does not exist
        """

    @abstractmethod
    def get_project_question_by_id(
        self, question_id: EntityId
    ) -> Optional[ProjectQuestion]:
        """Gets a question by its id
        :param question_id: the question id
        :return: the question or None if it does not exist"""

    @abstractmethod
    def insert_project_question(self, question: ProjectQuestion) -> EntityId:
        """Inserts a project question
        :param question: the question to insert
        :raises ConflictError: if the project already exists
        :raises ValueError: if the project does not exist"""
        pass

    @abstractmethod
    def update_project_question(
        self, question_id: EntityId, question: ProjectQuestion
    ) -> None:
        """Updates an existing project
        :param question_id: the id of the question to update
        :param question: the updated question
        :raises NotFoundError: if the question does not exist"""

    @abstractmethod
    def delete_project_question(self, question_id: EntityId) -> None:
        """Deletes a question
        :param question_id: the id of the question to delete
        :raises NotFoundError: if the question does not exist"""
        pass

    @abstractmethod
    def delete_questionnaire(self, project_id: EntityId):
        """
        Removes all questions from the questionnaire.
        :param project_id: the project id
        """
        pass

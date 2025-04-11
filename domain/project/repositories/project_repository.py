from abc import ABC, abstractmethod
from typing import List, Optional

from domain.common.core import EntityId
from domain.project.core import Project


class ProjectRepository(ABC):

    @abstractmethod
    def get_all_projects(self) -> List[Project]:
        """Gets all projects
        :return: a list of all projects"""
        pass

    @abstractmethod
    def get_project_by_id(self, project_id: EntityId) -> Optional[Project]:
        """Gets a project by its id
        :param project_id: the project id
        :return: the project or None if it does not exist"""
        pass

    @abstractmethod
    def insert_project(self, project) -> EntityId:
        """Inserts a project
        :param project: the project to insert
        :return: the id of the inserted project
        :raises ConflictError: if the project already exists"""
        pass

    @abstractmethod
    def update_project(self, project_id: EntityId, project) -> None:
        """Updates an existing project
        :param project_id: the id of the project to update
        :param project: the updated project
        :raises NotFoundError: if the project does not exist"""
        pass

    @abstractmethod
    def delete_project(self, project_id: EntityId) -> None:
        """Deletes a project
        :param project_id: the id of the project to delete
        :raises NotFoundError: if the project does not exist"""
        pass

    @abstractmethod
    def check_project_exists(self, project_id: EntityId) -> bool:
        """Checks if a project exists
        :param project_id: the project id
        :return: True if the project exists, False otherwise"""
        pass

    @abstractmethod
    def get_public_context(self) -> dict:
        """Gets the public context
        :return: the public context"""
        pass

    @abstractmethod
    def add_context_key(self, project_id: EntityId, key: str, value: str) -> None:
        """
        Adds a key to the project context
        :param project_id: the project id
        :param key: the key to add
        :param value: the value of the key
        :raises NotFoundError: if the project does not exist
        """

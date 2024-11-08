from typing import Optional, List

import shortuuid

from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.factories import ProjectFactory
from domain.project.repositories import ProjectRepository
from utils.errors import BadRequestError


class ProjectService:

    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    def get_all_projects(self) -> List[Project]:
        """
        Gets all projects
        :return: a list of all projects
        """
        return self.project_repository.get_all_projects()

    def get_project_by_id(self, project_id: EntityId) -> Optional[Project]:
        """
        Gets a project by its id
        :param project_id: the project id
        :return: the project or None if it does not exist
        """
        return self.project_repository.get_project_by_id(project_id)

    def add_project(self, name: str) -> EntityId:
        """
        Inserts a project
        :param name: the project name
        :return: the id of the inserted project
        :raises ConflictError: if the project already exists
        """
        project: Project = ProjectFactory.create_project(
            ProjectFactory.id_of(code=shortuuid.uuid()), name, {}
        )
        return self.project_repository.insert_project(project)

    def update_project(self, project_id: EntityId, project: Project) -> None:
        """
        Updates an existing project
        :param project_id: the id of the project to update
        :param project: the updated project
        :raises BadRequestError: if the project id does not match the existing project id
        :raises NotFoundError: if the project does not exist
        """
        if project_id != project.id:
            raise BadRequestError("Updated project id does not match")
        self.project_repository.update_project(project_id, project)

    def delete_project(self, project_id: EntityId) -> None:
        """
        Deletes a project
        :param project_id: the id of the project to delete
        :raises NotFoundError: if the project does not exist
        """
        self.project_repository.delete_project(project_id)

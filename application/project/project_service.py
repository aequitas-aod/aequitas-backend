import io
import re
import tempfile
from pathlib import Path
from typing import Optional, List, Union, Dict
from warnings import warn

import shortuuid

import utils.encodings as base64
from application.project.report import create_report_data, create_report
from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.factories import ProjectFactory
from domain.project.repositories import ProjectRepository
from utils.encodings import encode
from utils.errors import BadRequestError, NotFoundError


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

    def add_project(self, name: str, code: str = None) -> EntityId:
        """
        Inserts a project
        :param name: the project name
        :return: the id of the inserted project
        :raises ConflictError: if the project already exists
        """
        project: Project = ProjectFactory.create_project(
            ProjectFactory.id_of(code=code or shortuuid.uuid()), name, {}
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

    def check_project_exists(self, project_id: EntityId) -> bool:
        """
        Checks if a project exists
        :param project_id: the project id
        :return: True if the project exists, False otherwise
        """
        return self.project_repository.check_project_exists(project_id)

    def get_context(self, project_id: EntityId) -> Optional[dict]:
        """
        Gets the context of a project by its id, if the project does not exist returns None
        :param project_id: the project id
        :return: the project context or None if the project does not exist
        :raises NotFoundError: if the project does not exist
        """
        project: Optional[Project] = self.get_project_by_id(project_id)
        if project is not None:
            return project.get_context()
        raise NotFoundError("Project does not exist")

    def add_context_key(
        self, project_id: EntityId, key: str, value: Union[str, bytes]
    ) -> None:
        """
        Adds a key to the project context
        :param project_id: the project id
        :param key: the key to add
        :param value: the value of the key
        :raises NotFoundError: if the project does not exist
        :raises ValueError: if the value is not of type str or bytes
        """
        if type(value) != str and type(value) != bytes:
            raise ValueError(f"Value must be of type str or bytes, not {type(value)}")

        project: Optional[Project] = self.get_project_by_id(project_id)
        if project is None:
            raise NotFoundError("Project does not exist")
        self.project_repository.add_context_key(project_id, key, encode(value))

    @staticmethod
    def __bytes_to_string(value: bytes) -> tuple[str, bool]:
        try:
            return value.decode("utf-8"), False
        except UnicodeDecodeError:
            return base64.encode(value), True

    def get_from_context(
        self, project_id: EntityId, key: str
    ) -> Optional[tuple[str, bool]]:
        """
        Gets a value from the project context, if it is not found tries to get it from the public context
        :param project_id: the project id
        :param key: the key to get
        :return: the (value, binary) tuple where value is a string and binary is true if value represents a binary file in base64, or None if it does not exist
        """
        project: Optional[Project] = self.get_project_by_id(project_id)
        if project is not None:
            try:
                value: Union[str, bytes] = project.get_from_context(key)
            except ValueError:
                value: Union[str, bytes] = (
                    self.project_repository.get_public_context().get(key)
                )
            binary = isinstance(value, bytes)
            if binary:
                value, binary = self.__bytes_to_string(value)
            return value, binary
        raise NotFoundError("Project does not exist")

    def create_report(self, project_id: EntityId) -> io.BytesIO:
        """Creates the report of the experiment.

        :param project_id: the id of the project
        :return: the pdf report of the project
        """
        project = self.project_repository.get_project_by_id(project_id)
        public_context = self.project_repository.get_public_context()
        ctx = project.get_context() | public_context
        regex_patterns_for_report: Dict[re.Pattern, str] = {
            re.compile(r"^dataset_head__\w+-1$"): "Dataset View",
            re.compile(r"^stats__\w+-1$"): "Features View",
            re.compile(r"^correlation_matrix__\w+-1$"): "Proxies",
            re.compile(r"^suggested_proxies__\w+-1$"): "Proxies",
            re.compile(r"^metrics__\w+-1$"): "Detection",
            re.compile(r"^preprocessing__\w+$"): "Data Mitigation",
            re.compile(r"^preprocessing_plot__\w+-2$"): "Data Mitigation Results",
            re.compile(r"^performance_plot__\w+-2$"): "Data Mitigation Results",
            re.compile(r"^fairness_plot__\w+-2$"): "Data Mitigation Results",
            re.compile(r"^dataset_head__\w+-2$"): "Data Mitigation Results",
            re.compile(r"^correlation_matrix__\w+-2$"): "Data Mitigation Results",
            re.compile(r"^polarization_plot__[\w-]+__[\w-]+$"): "Stress Test Results",
            re.compile(r"^predictions_head__[\w-]+__[\w-]+$"): "Stress Test Results",
            re.compile(r"^correlation_matrix__[\w-]+__[\w-]+$"): "Stress Test Results",
            re.compile(r"^metrics__[\w-]+__[\w-]+$"): "Stress Test Results",
        }

        current_dataset: str = ctx.get("current_dataset")[:-2]
        ctx: dict = {key: value for key, value in ctx.items() if current_dataset in key}
        to_delete: List[str] = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for pattern, title in regex_patterns_for_report.items():
                for key, value in ctx.items():
                    if pattern.match(key):
                        to_delete.append(key)
                        if isinstance(value, bytes):
                            value = value.decode("utf-8")
                        create_report_data(temp_dir, title, {key: value})
                    else:
                        warn(
                            f"Pattern '{pattern}' did not match any key in the context.",
                            RuntimeWarning,
                        )
            print(to_delete)
            # file_name: str = f"report_{project_id.code}.pdf"
            file_name: str = f"report.pdf"
            create_report(temp_dir, file_name)
            print("Report created successfully")
            report_path = Path(temp_dir) / file_name
            # Create an in-memory file
            file_data: io.BytesIO = io.BytesIO(report_path.read_bytes())

            # You must seek back to start
            file_data.seek(0)
            return file_data

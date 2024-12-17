from typing import List, Set, Optional

from flask import Blueprint, request
from flask_restful import Api, Resource

from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.factories import ProjectFactory
from infrastructure.ws.setup import project_service, events_service
from infrastructure.ws.utils import logger
from presentation.presentation import serialize, deserialize
from utils.env import ENV
from utils.errors import ConflictError, NotFoundError, BadRequestError
from utils.status_code import StatusCode

projects_bp = Blueprint("projects", __name__)
api = Api(projects_bp)

projects: Set = set()


class ProjectResource(Resource):

    def get(self, project_id=None):
        if project_id:
            project: Optional[Project] = project_service.get_project_by_id(
                ProjectFactory.id_of(code=project_id)
            )
            if project:
                return serialize(project), StatusCode.OK
            else:
                return "Project not found", StatusCode.NOT_FOUND
        else:
            all_projects: List = project_service.get_all_projects()
            return [serialize(project) for project in all_projects], StatusCode.OK

    def post(self):
        body: dict = request.get_json()
        try:
            project_id: EntityId = project_service.add_project(body["name"])
        except ConflictError as e:
            return e.message, e.status_code
        return serialize(project_id), StatusCode.CREATED

    def put(self, project_id=None):
        if project_id:
            updated_project: Project = deserialize(request.get_json(), Project)
            try:
                project_service.update_project(
                    ProjectFactory.id_of(code=project_id), updated_project
                )
                return "Project updated successfully", StatusCode.OK
            except BadRequestError as e:
                return e.message, e.status_code
            except NotFoundError as e:
                return e.message, e.status_code
        else:
            return "Missing project id", StatusCode.BAD_REQUEST

    def delete(self, project_id=None):
        if project_id:
            try:
                project_service.delete_project(ProjectFactory.id_of(code=project_id))
                return "Project deleted successfully", StatusCode.OK
            except NotFoundError as e:
                return e.message, e.status_code
        else:
            return "Missing project id", StatusCode.BAD_REQUEST


class ProjectContextResource(Resource):

    def get(self, project_id=None):
        key = request.args.get("key")
        try:
            if key:
                value = project_service.get_from_context(
                    ProjectFactory.id_of(code=project_id), request.args.get("key")
                )
            else:
                value = project_service.get_context(
                    ProjectFactory.id_of(code=project_id)
                )
            return value, StatusCode.OK
        except NotFoundError:
            return "Project not found", StatusCode.NOT_FOUND

    def put(self, project_id=None):
        project: Optional[Project] = project_service.get_project_by_id(
            ProjectFactory.id_of(code=project_id)
        )
        if project:
            key = request.args.get("key")
            if not key:
                return "Missing key", StatusCode.BAD_REQUEST
            value: str = request.get_data(as_text=True)
            if not value:
                return "Missing value", StatusCode.BAD_REQUEST
            updated_project = project.add_to_context(key, value)
            project_service.update_project(
                ProjectFactory.id_of(code=project_id), updated_project
            )
            trigger_event(key, ProjectFactory.id_of(code=project_id))
            return "Project context updated successfully", StatusCode.OK
        else:
            return "Project not found", StatusCode.NOT_FOUND


api.add_resource(ProjectResource, "/projects", "/projects/<string:project_id>")
api.add_resource(ProjectContextResource, "/projects/<string:project_id>/context")


def trigger_event(context_key: str, project_id: EntityId) -> None:
    if ENV != "test":
        message = {"project_id": serialize(project_id)}
        if "dataset__" in context_key:
            message["context_key"] = context_key
            logger.error("PUBLISH DATASET " + str(message))
            events_service.publish_message("datasets.created", message)
        elif "features__" in context_key:
            # TODO: Implement the feature creation event
            events_service.publish_message("features.created", message)

from pydoc_data.topics import topics
from typing import List, Set, Optional

from flask import Blueprint, request
from flask_restful import Api, Resource

from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.factories import ProjectFactory
from infrastructure.ws.setup import project_service, events_service
from presentation.presentation import serialize, deserialize
from utils.env import ENV
from utils.errors import ConflictError, NotFoundError, BadRequestError
from utils.logs import logger
from utils.status_code import StatusCode
from typing import Iterable, Dict


projects_bp = Blueprint("projects", __name__)
api = Api(projects_bp)

projects: Set = set()


class EventGenerator:
    __primitive_types = (int, str, float, bool)

    def __serialize(self, obj):
        try:
            return serialize(obj)
        except ValueError as e:
            if any(isinstance(obj, t) for t in self.__primitive_types):
                return obj
            elif isinstance(obj, Dict):
                return {k: self.__serialize(v) for k, v in obj.items()}
            elif isinstance(obj, Iterable):
                return [self.__serialize(v) for v in obj]
            raise e

    @staticmethod
    def __wrap_notable_keys(**kwargs) -> Dict:
        data = dict(kwargs)
        if "project_id" in data:
            data["project_id"] = ProjectFactory.id_of(code=data["project_id"])
        return data

    def trigger_event(self, event_key: str, **kwargs):
        if ENV == "test":
            logger.debug(f"Skip triggering of event")
            return
        message = self.__serialize(self.__wrap_notable_keys(**kwargs))
        if "dataset__" in event_key:
            topic = "datasets.created"
        elif "features__" in event_key:
            topic = "features.created"
        else:
            raise ValueError(f"Unknown event key: {event_key}")
        events_service.publish_message(topic, message)
        logger.info(f"Trigger event on topic {topic} with message {message}")


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


class ProjectContextResource(Resource, EventGenerator):

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
            self.trigger_event(key, project_id=project_id, context_key=key)
            return "Project context updated successfully", StatusCode.OK
        else:
            return "Project not found", StatusCode.NOT_FOUND


api.add_resource(ProjectResource, "/projects", "/projects/<string:project_id>")
api.add_resource(ProjectContextResource, "/projects/<string:project_id>/context")

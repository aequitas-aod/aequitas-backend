from typing import List, Set, Optional

from flask import Blueprint, request
from flask_restful import Api, Resource

from domain.project.core import Project, ProjectId
from presentation.presentation import serialize, deserialize
from utils.errors import ConflictError, NotFoundError, BadRequestError
from utils.status_code import StatusCode
from infrastructure.ws.setup import project_service

projects_bp = Blueprint("projects", __name__)
api = Api(projects_bp)

projects: Set = set()


class ProjectResource(Resource):

    def get(self, project_id=None):
        if project_id:
            project: Optional[Project] = project_service.get_project_by_id(
                ProjectId(code=project_id)
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
            project_id: ProjectId = project_service.add_project(body["name"])
        except ConflictError as e:
            return e.message, e.status_code
        return serialize(project_id), StatusCode.CREATED

    def put(self, project_id=None):
        if project_id:
            updated_project: Project = deserialize(request.get_json(), Project)
            try:
                project_service.update_project(
                    ProjectId(code=project_id), updated_project
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
                project_service.delete_project(ProjectId(code=project_id))
                return "Project deleted successfully", StatusCode.OK
            except NotFoundError as e:
                return e.message, e.status_code
        else:
            return "Missing project id", StatusCode.BAD_REQUEST


class ProjectContextResource(Resource):

    def get(self, project_id):
        project: Optional[Project] = project_service.get_project_by_id(
            ProjectId(code=project_id)
        )
        if project:
            key = request.args.get("key")
            if not key:
                return project.context, StatusCode.OK
            else:
                return project.context.get(key), StatusCode.OK
        else:
            return "Project not found", StatusCode.NOT_FOUND

    def put(self, project_id):
        project: Optional[Project] = project_service.get_project_by_id(
            ProjectId(code=project_id)
        )
        if project:
            key = request.args.get("key")
            if not key:
                return "Missing key", StatusCode.BAD_REQUEST
            value: str = request.get_json()
            if not value:
                return "Missing value", StatusCode.BAD_REQUEST
            updated_project = project.add_to_context(key, value)
            project_service.update_project(ProjectId(code=project_id), updated_project)
            return "Project context updated successfully", StatusCode.OK
        else:
            return "Project not found", StatusCode.NOT_FOUND


api.add_resource(ProjectResource, "/projects", "/projects/<string:project_id>")
api.add_resource(ProjectContextResource, "/projects/<string:project_id>/context")

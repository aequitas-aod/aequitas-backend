import time
from datetime import datetime, timedelta
from typing import Set, Optional

from flask import Blueprint, request, Response
from flask_restful import Api, Resource

from infrastructure.ws.resources import EventGenerator
from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.factories import ProjectFactory
from infrastructure.ws.setup import project_service, events_service
from presentation.presentation import serialize, deserialize
from utils.encodings import encode
from utils.errors import ConflictError, NotFoundError, BadRequestError
from utils.logs import logger
from utils.status_code import StatusCode
import threading


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
            all_projects = project_service.get_all_projects()
            all_projects.sort(key=lambda p: p.id)
            logger.info("All projects retrieved: %s", [p.id.code for p in all_projects])
            return [serialize(project) for project in all_projects], StatusCode.OK

    def post(self):
        body: dict = request.get_json()
        try:
            project_id: EntityId = project_service.add_project(body["name"])
        except ConflictError as e:
            return e.message, e.status_code
        logger.info("Project '%s' created with id %s", body["name"], project_id.code)
        return serialize(project_id), StatusCode.CREATED

    def put(self, project_id=None):
        if project_id:
            updated_project: Project = deserialize(request.get_json(), Project)
            project_id = ProjectFactory.id_of(code=project_id)
            try:
                project_service.update_project(project_id, updated_project)
                logger.info("Project '%s' updated", project_id.code)
                return "Project updated successfully", StatusCode.OK
            except BadRequestError as e:
                return e.message, e.status_code
            except NotFoundError as e:
                return e.message, e.status_code
        else:
            return "Missing project id", StatusCode.BAD_REQUEST

    def delete(self, project_id=None):
        if project_id:
            project_id = ProjectFactory.id_of(code=project_id)
            try:
                project_service.delete_project(project_id)
                logger.info("Project '%s' deleted", project_id.code)
                return "Project deleted successfully", StatusCode.OK
            except NotFoundError as e:
                return e.message, e.status_code
        else:
            return "Missing project id", StatusCode.BAD_REQUEST


class ProjectContextResource(Resource, EventGenerator):
    SLEEP_TIME = timedelta(seconds=1)
    LOG_ONCE_EVERY = 10  # seconds
    DEFAULT_TIMEOUT = timedelta(minutes=5)

    def _try_get_key(
        self, project_id: EntityId, key: str, silent_miss=False
    ) -> Response:
        value, base64 = project_service.get_from_context(project_id, key)
        if value:
            logger.info("Key '%s' found in project '%s'", key, project_id.code)
            return Response(
                value,
                status=StatusCode.OK,
                content_type=("application/binary-octet" if base64 else "plain/text"),
            )
        else:
            if not silent_miss:
                logger.warn("Key '%s' not found in project '%s'", key, project_id.code)
            return Response("Key not found", StatusCode.NOT_FOUND)

    def _get_key(self, project_id: EntityId, key: str, timeout: timedelta) -> Response:
        # FIXME this is blocking implementation. better would be to use async programming,
        #  and tracking suspended, resuming then upon put
        waiting_unlogged = True
        init = datetime.now()
        next_log_at = self.LOG_ONCE_EVERY
        while (elapsed := datetime.now() - init) < timeout:
            response = self._try_get_key(project_id, key, silent_miss=True)
            if response.status_code == StatusCode.OK:
                return response
            elif waiting_unlogged:
                logger.info(
                    "On thread %s, start waiting for key '%s' in project '%s', timeout in %g seconds",
                    threading.current_thread().name,
                    key,
                    project_id.code,
                    timeout.total_seconds(),
                )
                waiting_unlogged = False
            elif elapsed.total_seconds() / self.LOG_ONCE_EVERY >= next_log_at:
                logger.debug(
                    "On thread %s, still waiting for key '%s' in project '%s', %g seconds elapsed over %g",
                    threading.current_thread().name,
                    key,
                    project_id.code,
                    elapsed.total_seconds(),
                    timeout.total_seconds(),
                )
                next_log_at += self.LOG_ONCE_EVERY
            time.sleep(self.SLEEP_TIME.total_seconds())
        return Response("Key not found in time", StatusCode.REQUEST_TIMEOUT)

    def _get_all(self, project_id: EntityId) -> tuple:
        value = project_service.get_context(project_id)
        logger.info("Context of project '%s' retrieved", project_id.code)
        value = {k: v if isinstance(v, str) else encode(v) for k, v in value.items()}
        return value, StatusCode.OK, {"Content-Type": "application/json"}

    def _parse_optional_bool(self, name: str, default: bool) -> bool:
        raw = request.args.get(name, default=str(default)).lower()
        if raw in ("true", "1"):
            return True
        elif raw in ("false", "0"):
            return False
        else:
            raise BadRequestError(f"Invalid value for parameter {name}: {raw}")

    def get(self, project_id=None):
        key = request.args.get("key")
        project_id = ProjectFactory.id_of(code=project_id)
        try:
            if key:
                wait = self._parse_optional_bool("wait", default=True)
                if wait:
                    timeout = request.args.get("timeout", default=0.0, type=float)
                    if timeout <= 0.0:
                        timeout = self.DEFAULT_TIMEOUT
                    else:
                        timeout = timedelta(seconds=timeout)
                    return self._get_key(project_id, key, timeout)
                return self._try_get_key(project_id, key)
            else:
                return self._get_all(project_id)
        except NotFoundError:
            return "Project not found", StatusCode.NOT_FOUND

    def put(self, project_id=None):
        project_id = ProjectFactory.id_of(code=project_id)
        project = project_service.get_project_by_id(project_id)
        if project:
            key = request.args.get("key")
            if not key:
                return "Missing key", StatusCode.BAD_REQUEST
            value: bytes = request.get_data()
            if not value:
                return "Missing value", StatusCode.BAD_REQUEST
            updated_project = project.add_to_context(key, value)
            project_service.update_project(project_id, updated_project)
            logger.info("Key '%s' updated in project '%s'", key, project_id.code)
            self.trigger_context_event(key, project_id=project_id.code, context_key=key)
            return "Project context updated successfully", StatusCode.OK
        else:
            return "Project not found", StatusCode.NOT_FOUND


api.add_resource(ProjectResource, "/projects", "/projects/<string:project_id>")
api.add_resource(ProjectContextResource, "/projects/<string:project_id>/context")

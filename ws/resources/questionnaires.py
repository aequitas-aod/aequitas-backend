from typing import Optional, List

from flask import Blueprint, request
from flask_restful import Api, Resource

from domain.common.core import AnswerId
from domain.project.core import ProjectId, ProjectQuestion
from presentation.presentation import serialize
from utils.errors import NotFoundError, BadRequestError
from utils.status_code import StatusCode
from ws.setup import questionnaire_service

questionnaires_bp = Blueprint("questionnaires", __name__)
api = Api(questionnaires_bp)


class QuestionnaireResource(Resource):
    def get(self, project_id, index=None):
        if index:
            try:
                q: Optional[ProjectQuestion] = questionnaire_service.get_nth_question(
                    ProjectId(code=project_id), index
                )
                return serialize(q), StatusCode.OK
            except NotFoundError as e:
                return e.message, StatusCode.NOT_FOUND
            except BadRequestError as e:
                return e.message, StatusCode.BAD_REQUEST
        else:
            questionnaire: List[ProjectQuestion] = (
                questionnaire_service.get_questionnaire(ProjectId(code=project_id))
            )
            return [serialize(q) for q in questionnaire], StatusCode.OK

    def put(self, project_id, index=None):
        if index is None:
            return "Missing question index", StatusCode.BAD_REQUEST
        else:
            answer_ids_json = request.get_json()["answer_ids"]
            answer_ids: List[AnswerId] = [
                AnswerId(code=code) for code in answer_ids_json
            ]
            try:
                questionnaire_service.select_answers(
                    ProjectId(code=project_id), index, answer_ids
                )
            except ValueError:
                return (
                    "Answer selected is not in the set of available answers",
                    StatusCode.BAD_REQUEST,
                )
            return "Answer selected successfully", StatusCode.OK

    def delete(self, project_id, index=None):
        if index is None:
            questionnaire_service.reset_questionnaire(ProjectId(code=project_id))
            return "Questionnaire reset successfully", StatusCode.OK
        else:
            try:
                questionnaire_service.remove_question(ProjectId(code=project_id), index)
                return "Question removed successfully", StatusCode.OK
            except ValueError as e:
                return (
                    e.args[0],
                    StatusCode.BAD_REQUEST,
                )


api.add_resource(
    QuestionnaireResource,
    "/projects/<string:project_id>/questionnaire",
    "/projects/<string:project_id>/questionnaire/<int:index>",
)

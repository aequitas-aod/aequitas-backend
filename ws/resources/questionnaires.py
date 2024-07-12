from typing import Optional, List

from flask import Blueprint
from flask_restful import Api, Resource

from domain.project.core import ProjectId, ProjectQuestion
from presentation.presentation import serialize
from utils.status_code import StatusCode
from ws.setup import questionnaire_service

questionnaires_bp = Blueprint("questionnaires", __name__)
api = Api(questionnaires_bp)


class QuestionnaireResource(Resource):
    def get(self, project_id=None, index=None):
        if project_id is None:
            return "Missing project id", StatusCode.BAD_REQUEST
        if index:
            q: Optional[ProjectQuestion] = questionnaire_service.get_nth_question(
                ProjectId(code=project_id), index
            )
            if q:
                return serialize(q), StatusCode.OK
            else:
                return "Question not found", StatusCode.NOT_FOUND
        else:
            questionnaire: List[ProjectQuestion] = (
                questionnaire_service.get_questionnaire(ProjectId(code=project_id))
            )
            return [serialize(q) for q in questionnaire], StatusCode.OK

    def delete(self, project_id=None, index=None):
        # Replace this with business logic
        return "", 404


api.add_resource(
    QuestionnaireResource, "/projects/<string:project_id>/questionnaire/<int:index>"
)

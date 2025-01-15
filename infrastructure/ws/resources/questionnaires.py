from typing import Optional, List

from flask import Blueprint, request
from flask_restful import Api, Resource

from domain.common.core import EntityId
from domain.project.core import ProjectQuestion
from domain.project.factories import ProjectFactory
from infrastructure.ws.setup import questionnaire_service
from infrastructure.ws.resources import EventGenerator
from presentation.presentation import serialize, deserialize
from utils.errors import NotFoundError, BadRequestError
from utils.status_code import StatusCode

questionnaires_bp = Blueprint("questionnaires", __name__)
api = Api(questionnaires_bp)


class QuestionnaireResource(Resource, EventGenerator):
    def get(self, project_code, index=None):
        project_id: EntityId = ProjectFactory.id_of(code=project_code)
        if index:
            try:
                q: Optional[ProjectQuestion] = questionnaire_service.get_nth_question(
                    project_id, index
                )
                return serialize(q), StatusCode.OK
            except NotFoundError as e:
                return e.message, StatusCode.NOT_FOUND
            except BadRequestError as e:
                return e.message, StatusCode.BAD_REQUEST
        else:
            questionnaire: List[ProjectQuestion] = (
                questionnaire_service.get_questionnaire(project_id)
            )
            questionnaire.sort(key=lambda q: q.id)
            return [serialize(q) for q in questionnaire], StatusCode.OK

    def put(self, project_code, index=None):
        if index is None:
            return "Missing question index", StatusCode.BAD_REQUEST
        else:
            answer_ids_json = request.get_json()["answer_ids"]
            try:
                answer_ids: List[EntityId] = [
                    deserialize(project_answer_id, EntityId)
                    for project_answer_id in answer_ids_json
                ]
                project_id = ProjectFactory.id_of(code=project_code)
                questionnaire_service.select_answers(project_id, index, answer_ids)
                self.trigger_event(
                    "questionnaire.answered",
                    project_id=project_id,
                    question_index=index,
                    selected_answers_ids=list(answer_ids),
                )
            except ValueError:
                return (
                    "Answer selected is not in the set of available answers",
                    StatusCode.BAD_REQUEST,
                )
            except TypeError:
                return "Wrong id format", StatusCode.BAD_REQUEST
            return "Answer selected successfully", StatusCode.OK

    def delete(self, project_code, index=None):
        project_id: EntityId = ProjectFactory.id_of(code=project_code)
        if index is None:
            questionnaire_service.reset_questionnaire(project_id)
            return "Questionnaire reset successfully", StatusCode.OK
        else:
            try:
                questionnaire_service.remove_question(project_id, index)
                return "Question removed successfully", StatusCode.OK
            except ValueError as e:
                return (
                    e.args[0],
                    StatusCode.BAD_REQUEST,
                )


api.add_resource(
    QuestionnaireResource,
    "/projects/<string:project_code>/questionnaire",
    "/projects/<string:project_code>/questionnaire/<int:index>",
)

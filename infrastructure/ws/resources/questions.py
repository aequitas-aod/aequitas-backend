from typing import List, Optional

import yaml
from flask import Blueprint, request
from flask_restful import Api, Resource

from domain.common.core import EntityId
from domain.graph.core import GraphQuestion
from domain.graph.factories import GraphQuestionFactory
from infrastructure.ws.setup import question_service
from presentation.presentation import serialize, deserialize
from utils.errors import BadRequestError, ConflictError, NotFoundError
from utils.status_code import StatusCode

questions_bp = Blueprint("questions", __name__)
api = Api(questions_bp)


class QuestionResource(Resource):

    def get(self, question_code=None):
        if question_code:
            graph_question_id: EntityId = GraphQuestionFactory.id_of(code=question_code)
            question: Optional[GraphQuestion] = question_service.get_question_by_id(
                graph_question_id
            )
            if question:
                return serialize(question), StatusCode.OK
            else:
                return "Question not found", StatusCode.NOT_FOUND
        else:
            all_questions: List = question_service.get_all_questions()
            all_questions.sort(key=lambda q: q.id)
            return [serialize(question) for question in all_questions], StatusCode.OK

    def post(self):
        new_question: GraphQuestion = deserialize(request.get_json(), GraphQuestion)
        try:
            question_service.add_question(new_question)
        except ConflictError as e:
            return e.message, e.status_code
        return serialize(new_question.id), StatusCode.CREATED

    def put(self, question_code=None):
        if question_code:
            updated_question: GraphQuestion = deserialize(
                request.get_json(), GraphQuestion
            )
            graph_question_id: EntityId = GraphQuestionFactory.id_of(code=question_code)
            try:
                question_service.update_question(graph_question_id, updated_question)
                return "Question updated successfully", StatusCode.OK
            except BadRequestError as e:
                return e.message, e.status_code
            except NotFoundError as e:
                return e.message, e.status_code
        else:
            return "Missing question id", StatusCode.BAD_REQUEST

    def delete(self, question_code=None):
        if question_code:
            graph_question_id: EntityId = GraphQuestionFactory.id_of(code=question_code)
            try:
                question_service.delete_question(graph_question_id)
                return "Question deleted successfully", StatusCode.OK
            except NotFoundError as e:
                return e.message, e.status_code
        else:
            return "Missing question id", StatusCode.BAD_REQUEST


class NewCandidateID(Resource):

    def get(self):
        return serialize(question_service.get_new_candidate_id())


class LastInsertedQuestion(Resource):

    def get(self):
        last_inserted_question: Optional[GraphQuestion] = (
            question_service.get_last_inserted_question()
        )
        if last_inserted_question:
            return serialize(last_inserted_question), StatusCode.OK
        else:
            return "No questions found", StatusCode.NOT_FOUND


class LoadQuestions(Resource):

    def post(self):
        if not request.data:
            return {"error": "No data provided"}, StatusCode.BAD_REQUEST

        if request.content_type != "text/yaml":
            return {
                "error": "Unsupported media type"
            }, StatusCode.UNSUPPORTED_MEDIA_TYPE

        try:
            questions_dict: dict = yaml.safe_load(request.data)
            for question in questions_dict:
                question_service.add_question(deserialize(question, GraphQuestion))
            return "Questions loaded successfully", StatusCode.CREATED
        except yaml.YAMLError:
            return {"error": "Invalid YAML file"}, StatusCode.BAD_REQUEST


api.add_resource(QuestionResource, "/questions", "/questions/<string:question_code>")
api.add_resource(NewCandidateID, "/questions/new-candidate-id")
api.add_resource(LastInsertedQuestion, "/questions/last-inserted")
api.add_resource(LoadQuestions, "/questions/load")

import unittest
from datetime import datetime

from domain.common.core import EntityId
from domain.common.core.enum import QuestionType
from domain.common.factories import AnswerFactory
from domain.graph.core import GraphQuestion
from domain.graph.core.enum import Action
from domain.graph.factories import GraphQuestionFactory
from presentation.presentation import deserialize, serialize


class TestGraphQuestionPresentation(unittest.TestCase):

    def setUp(self):
        self.question_timestamp = datetime.now()
        self.graph_question_id: EntityId = GraphQuestionFactory.id_of(
            code="boolean_question_id"
        )
        self.answer_id: EntityId = AnswerFactory.id_of(
            code="answer-code", question_id=self.graph_question_id
        )
        self.question: GraphQuestion = GraphQuestionFactory.create_boolean_question(
            self.graph_question_id,
            "Do you practice TDD?",
            "Question description",
            created_at=self.question_timestamp,
            enabled_by=frozenset({self.answer_id}),
            action_needed=Action.METRICS_CHECK,
        )
        self.question_dict: dict = {
            "id": {"code": "boolean_question_id"},
            "text": "Do you practice TDD?",
            "description": "Question description",
            "type": QuestionType.BOOLEAN.value,
            "answers": [
                {
                    "id": {
                        "code": "boolean_question_id-false",
                        "question_code": "boolean_question_id",
                    },
                    "text": "No",
                    "description": None,
                },
                {
                    "id": {
                        "code": "boolean_question_id-true",
                        "question_code": "boolean_question_id",
                    },
                    "text": "Yes",
                    "description": None,
                },
            ],
            "enabled_by": [
                {"code": "answer-code", "question_code": "boolean_question_id"}
            ],
            "action_needed": Action.METRICS_CHECK.value,
            "created_at": self.question_timestamp.isoformat(),
        }

    def test_deserialize_graph_question(self):
        actual: GraphQuestion = deserialize(self.question_dict, GraphQuestion)
        self.assertEqual(
            self.question,
            actual,
        )

    def test_serialize_question(self):
        actual: dict = serialize(self.question)
        self.assertEqual(
            self.question_dict,
            actual,
        )

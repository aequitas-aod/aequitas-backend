import unittest
from datetime import datetime

from domain.common.core import AnswerId, QuestionId
from domain.common.core.enum import QuestionType
from domain.graph.core import GraphQuestion
from domain.graph.core.enum import Action
from domain.graph.factories import GraphQuestionFactory
from presentation.presentation import deserialize, serialize


class TestGraphQuestionPresentation(unittest.TestCase):

    def setUp(self):
        self.question_timestamp = datetime.now()
        self.question: GraphQuestion = GraphQuestionFactory.create_boolean_question(
            QuestionId(code="boolean_question_id"),
            "Do you practice TDD?",
            created_at=self.question_timestamp,
            enabled_by=frozenset({AnswerId(code="answer-code")}),
            action_needed=Action.METRICS_CHECK,
        )
        self.question_dict: dict = {
            "id": {"code": "boolean_question_id"},
            "text": "Do you practice TDD?",
            "type": QuestionType.BOOLEAN.value,
            "answers": [
                {
                    "id": {"code": "boolean_question_id-false"},
                    "text": "No",
                    "description": None,
                },
                {
                    "id": {"code": "boolean_question_id-true"},
                    "text": "Yes",
                    "description": None,
                },
            ],
            "enabled_by": [{"code": "answer-code"}],
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

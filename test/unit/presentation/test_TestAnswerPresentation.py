import unittest

from domain.common.core import Answer, EntityId
from domain.common.factories import AnswerFactory
from domain.graph.factories import GraphQuestionFactory
from presentation.presentation import serialize, deserialize


class TestAnswerPresentation(unittest.TestCase):

    def setUp(self):
        self.question_id: EntityId = GraphQuestionFactory.id_of(code="question")
        self.answer: Answer = AnswerFactory.create_answer(
            AnswerFactory.id_of(code="answer", question_id=self.question_id), "Always."
        )
        self.answer_dict: dict = {
            "id": {"code": "answer", "question_code": "question"},
            "text": "Always.",
            "description": None,
        }
        self.boolean_answer: Answer = AnswerFactory.create_boolean_answer(
            AnswerFactory.id_of(code="boolean-answer", question_id=self.question_id),
            False,
        )
        self.boolean_answer_dict: dict = {
            "id": {"code": "boolean-answer", "question_code": "question"},
            "text": "No",
            "description": None,
        }

    def test_serialize_answer(self):
        actual: dict = serialize(self.answer)
        self.assertEqual(
            self.answer_dict,
            actual,
        )

    def test_deserialize_answer(self):
        actual: Answer = deserialize(self.answer_dict, Answer)
        self.assertEqual(
            self.answer,
            actual,
        )

    def test_serialize_boolean_answer(self):
        actual: dict = serialize(self.boolean_answer)
        self.assertEqual(
            self.boolean_answer_dict,
            actual,
        )

    def test_deserialize_boolean_answer(self):
        actual: Answer = deserialize(self.boolean_answer_dict, Answer)
        self.assertEqual(
            self.boolean_answer,
            actual,
        )

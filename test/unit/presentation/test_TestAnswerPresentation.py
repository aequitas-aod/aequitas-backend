import unittest

from domain.common.core import Answer, AnswerId
from domain.common.factories import AnswerFactory
from presentation.presentation import serialize, deserialize


class TestAnswerPresentation(unittest.TestCase):

    def setUp(self):
        self.answer: Answer = AnswerFactory.create_answer(
            AnswerId(code="answer"), "Always."
        )
        self.answer_dict: dict = {
            "id": {"code": "answer"},
            "text": "Always.",
            "description": None,
        }
        self.boolean_answer: Answer = AnswerFactory.create_boolean_answer(
            AnswerId(code="boolean-answer"), False
        )
        self.boolean_answer_dict: dict = {
            "id": {"code": "boolean-answer"},
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

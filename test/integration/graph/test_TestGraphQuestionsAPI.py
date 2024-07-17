# import json
# import unittest
# from datetime import datetime
# from pathlib import Path
# from typing import Set
#
# import yaml
# from python_on_whales import DockerClient
#
# from domain.common.core import QuestionId, AnswerId
# from domain.common.factories import AnswerFactory
# from domain.graph.core import GraphQuestion
# from domain.common.core.enum import QuestionType
# from domain.graph.factories import GraphQuestionFactory
# from presentation.presentation import serialize, deserialize
# from test.utils.utils import get_file_path
# from ws.main import create_app
#
#
# class TestGraphQuestionsAPI(unittest.TestCase):
#
#     @classmethod
#     def startDocker(cls):
#         cls.docker = DockerClient()
#         cls.docker.compose.down(volumes=True)
#         cls.docker.compose.up(detach=True, wait=True)
#
#     @classmethod
#     def setUpClass(cls):
#         cls.startDocker()
#         cls.app = create_app().test_client()
#         cls.question_timestamp = datetime.now()
#         cls.question_timestamp_2 = datetime.now()
#         cls.question: GraphQuestion = GraphQuestionFactory.create_question(
#             QuestionId(code="test-question"),
#             "Test question",
#             QuestionType.SINGLE_CHOICE,
#             frozenset(
#                 {
#                     AnswerFactory.create_answer(AnswerId(code="answer-yes"), "Yes"),
#                     AnswerFactory.create_answer(
#                         AnswerId(code="answer-little-bit"), "A little bit"
#                     ),
#                     AnswerFactory.create_answer(AnswerId(code="answer-no"), "No"),
#                 }
#             ),
#             created_at=cls.question_timestamp,
#         )
#         cls.question2: GraphQuestion = GraphQuestionFactory.create_boolean_question(
#             QuestionId(code="test-question-2"),
#             "Test question 2",
#             created_at=cls.question_timestamp_2,
#         )
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.docker.compose.down(volumes=True)
#
#     def tearDown(self):
#         self._delete_all_questions()
#
#     def _delete_all_questions(self):
#         response = self.app.get("/questions")
#         questions_dict = json.loads(response.data)
#         for question in questions_dict:
#             self.app.delete(f"/questions/{question['id']['code']}")
#
#     def test_get_all_questions(self):
#         self.app.post("/questions", json=serialize(self.question))
#         self.app.post("/questions", json=serialize(self.question2))
#         response = self.app.get("/questions")
#         questions_dict = json.loads(response.data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(2, len(questions_dict))
#         all_questions: Set[GraphQuestion] = set(
#             [deserialize(question, GraphQuestion) for question in questions_dict]
#         )
#         self.assertEqual({self.question, self.question2}, all_questions)
#
#     def test_get_question(self):
#         self.app.post("/questions", json=serialize(self.question))
#         response = self.app.get(f"/questions/{self.question.id.code}")
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(
#             self.question, deserialize(json.loads(response.data), GraphQuestion)
#         )
#
#     def test_get_non_existent_question(self):
#         response = self.app.get("/questions/does-not-exist")
#         self.assertEqual(response.status_code, 404)
#
#     def test_insert_question(self):
#         response = self.app.post("/questions", json=serialize(self.question))
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(
#             self.question.id, deserialize(json.loads(response.data), QuestionId)
#         )
#
#     def test_insert_duplicate_question(self):
#         self.app.post("/questions", json=serialize(self.question))
#         response = self.app.post("/questions", json=serialize(self.question))
#         self.assertEqual(response.status_code, 409)
#
#     def test_update_question(self):
#         self.app.post("/questions", json=serialize(self.question))
#         updated_question: GraphQuestion = self.question.model_copy()
#         updated_question.text = "Updated text"
#         updated_question.type = QuestionType.MULTIPLE_CHOICE
#         response = self.app.put(
#             f"/questions/{self.question.id.code}", json=serialize(updated_question)
#         )
#         self.assertEqual(response.status_code, 200)
#         response = self.app.get(f"/questions/{self.question.id.code}")
#         self.assertEqual(
#             updated_question, deserialize(json.loads(response.data), GraphQuestion)
#         )
#         response = self.app.put(
#             f"/questions/{self.question2.id.code}", json=serialize(self.question)
#         )
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(
#             json.loads(response.data), "Updated question id does not match"
#         )
#
#     def test_delete_question(self):
#         self.app.post("/questions", json=serialize(self.question))
#         response = self.app.delete(f"/questions/{self.question.id.code}")
#         self.assertEqual(response.status_code, 200)
#         response = self.app.get(f"/questions/{self.question.id.code}")
#         self.assertEqual(response.status_code, 404)
#
#     def test_delete_non_existent_question(self):
#         response = self.app.delete("/questions/does-not-exist")
#         self.assertEqual(response.status_code, 404)
#
#     def test_get_new_candidate_id(self):
#         response = self.app.get("/questions/new-candidate-id")
#         self.assertEqual(response.status_code, 200)
#         expected_question_id = serialize(QuestionId(code="q-1"))
#         self.assertEqual(expected_question_id, json.loads(response.data))
#         self.app.post("/questions", json=serialize(self.question))
#         response = self.app.get("/questions/new-candidate-id")
#         self.assertEqual(response.status_code, 200)
#         expected_question_id = serialize(QuestionId(code="q-2"))
#         self.assertEqual(expected_question_id, json.loads(response.data))
#
#     def test_get_new_candidate_id_after_deletion(self):
#         self.app.post("/questions", json=serialize(self.question))
#         self.app.delete(f"/questions/{self.question.id.code}")
#         response = self.app.get("/questions/new-candidate-id")
#         self.assertEqual(response.status_code, 200)
#         expected_question_id = serialize(QuestionId(code="q-1"))
#         self.assertEqual(expected_question_id, json.loads(response.data))
#
#     def test_last_inserted_question(self):
#         self.app.post("/questions", json=serialize(self.question))
#         response = self.app.get("/questions/last-inserted")
#         self.assertEqual(response.status_code, 200)
#         expected_question = serialize(self.question)
#         self.assertEqual(expected_question, json.loads(response.data))
#         self.app.post("/questions", json=serialize(self.question2))
#         response = self.app.get("/questions/last-inserted")
#         self.assertEqual(response.status_code, 200)
#         expected_question = serialize(self.question2)
#         self.assertEqual(expected_question, json.loads(response.data))
#
#     def test_questions_load(self):
#         yaml_file_path = get_file_path("test/resources/questions-load-example.yml")
#         with yaml_file_path.open("r") as file:
#             questions_yaml: str = file.read()
#             response = self.app.post(
#                 "/questions/load", content_type="text/yaml", data=questions_yaml
#             )
#             self.assertEqual(response.status_code, 201)
#             response = self.app.get("/questions")
#             self.assertEqual(response.status_code, 200)
#             expected_questions: dict = yaml.safe_load(questions_yaml)
#             self.assertEqual(expected_questions, json.loads(response.data))

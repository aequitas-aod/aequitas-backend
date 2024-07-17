import json
import unittest

import yaml
from python_on_whales import DockerClient

from domain.graph.core import GraphQuestion
from domain.project.core import ProjectId, ProjectQuestion
from presentation.presentation import deserialize
from test.utils.utils import get_file_path
from ws.main import create_app


class TestQuestionnairesAPI(unittest.TestCase):

    @classmethod
    def startDocker(cls):
        cls.docker = DockerClient()
        cls.docker.compose.down(volumes=True)
        cls.docker.compose.up(detach=True, wait=True)

    @classmethod
    def setUpClass(cls):
        cls.startDocker()
        cls.app = create_app().test_client()
        cls.project_name: str = "Project name"
        res = cls.app.post("/projects", json={"name": cls.project_name})
        cls.project_id: ProjectId = deserialize(json.loads(res.data), ProjectId)
        yaml_file_path = get_file_path("test/resources/question-graph-example.yml")
        with yaml_file_path.open("r") as file:
            questions_yaml: str = file.read()
            cls.app.post(
                "/questions/load", content_type="text/yaml", data=questions_yaml
            )
            cls.questions: list[GraphQuestion] = [
                deserialize(q, GraphQuestion) for q in yaml.safe_load(questions_yaml)
            ]

    @classmethod
    def tearDownClass(cls):
        # cls.docker.compose.down(volumes=True)
        pass

    def _compare_graph_and_project_questions(self, q1: ProjectQuestion, q2: GraphQuestion):
        self.assertEqual(q1.id.code, f"{self.project_id.code}-{q2.id.code}")
        self.assertEqual(q1.text, q2.text)
        self.assertEqual(q1.type, q2.type)
        self.assertEqual(
            frozenset([a.text for a in q1.answers]),
            frozenset([a.text for a in q2.answers]),
        )

    def test_01_get_first_question(self):
        first_question, related_question = self._get_question_from_questionnaire_and_graph(1)
        self._compare_graph_and_project_questions(first_question, related_question)

    def test_02_select_answer_to_first_question(self):
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/1")
        self.assertEqual(response.status_code, 200)
        first_question: ProjectQuestion = deserialize(
            json.loads(response.data), ProjectQuestion
        )
        answer = next(iter(first_question.answers))
        expected_question: ProjectQuestion = first_question.select_answer(answer.id)
        response = self.app.put(
            f"/projects/{self.project_id.code}/questionnaire/1",
            json={"answer_ids": [answer.id.code]},
        )
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/1")
        self.assertEqual(response.status_code, 200)
        selected_question: ProjectQuestion = deserialize(
            json.loads(response.data), ProjectQuestion
        )
        self.assertEqual(set(selected_question.answers), set(expected_question.answers))

    def test_03_select_wrong_answer(self):
        response = self.app.put(
            f"/projects/{self.project_id.code}/questionnaire/1",
            json={"answer_ids": ["not-existing"]},
        )
        self.assertEqual(response.status_code, 400)

    # def test_remove_question(self):
    #     response = self.app.delete(f"/projects/{self.project_id.code}/questionnaire/1")
    #     self.assertEqual(response.status_code, 200)
    #     response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/1")
    #     self.assertEqual(response.status_code, 400)

    def test_04_get_second_question(self):
        second_question, related_question = self._get_question_from_questionnaire_and_graph(2)
        self._compare_graph_and_project_questions(second_question, related_question)

    def test_05_select_answer_to_second_question(self):
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/2")
        self.assertEqual(response.status_code, 200)
        first_question: ProjectQuestion = deserialize(
            json.loads(response.data), ProjectQuestion
        )
        answer = next(iter(first_question.answers))
        expected_question: ProjectQuestion = first_question.select_answer(answer.id)
        response = self.app.put(
            f"/projects/{self.project_id.code}/questionnaire/2",
            json={"answer_ids": [answer.id.code]},
        )
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/2")
        self.assertEqual(response.status_code, 200)
        selected_question: ProjectQuestion = deserialize(
            json.loads(response.data), ProjectQuestion
        )
        self.assertEqual(set(selected_question.answers), set(expected_question.answers))

    def test_06_get_third_question(self):
        third_question, related_question = self._get_question_from_questionnaire_and_graph(3)
        self._compare_graph_and_project_questions(third_question, related_question)

    def _get_question_from_questionnaire_and_graph(self, index: int) -> (ProjectQuestion, GraphQuestion):
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/{index}")
        self.assertEqual(response.status_code, 200)
        project_question: ProjectQuestion = deserialize(
            json.loads(response.data), ProjectQuestion
        )
        response = self.app.get(f"questions/{self.questions[index - 1].id.code}")
        related_question: GraphQuestion = deserialize(
            json.loads(response.data), GraphQuestion
        )
        return project_question, related_question

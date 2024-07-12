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
        cls.docker.compose.down(volumes=True)

    def test_get_first_question(self):
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/1")
        self.assertEqual(response.status_code, 200)
        first_question: ProjectQuestion = deserialize(
            json.loads(response.data), ProjectQuestion
        )
        response = self.app.get(f"questions/{self.questions[0].id.code}")
        related_question: GraphQuestion = deserialize(
            json.loads(response.data), GraphQuestion
        )
        self.assertEqual(
            first_question.id.code, f"{self.project_id.code}-{related_question.id.code}"
        )
        self.assertEqual(first_question.text, related_question.text)
        self.assertEqual(first_question.type, related_question.type)
        self.assertEqual(
            frozenset([a.text for a in first_question.answers]),
            frozenset([a.text for a in related_question.answers]),
        )

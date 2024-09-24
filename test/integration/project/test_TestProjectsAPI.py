import json
import unittest
from typing import Set

from python_on_whales import DockerClient

from domain.project.core import Project, ProjectId
from presentation.presentation import deserialize, serialize
from ws.main import create_app


class TestProjectsAPI(unittest.TestCase):

    @classmethod
    def startDocker(cls):
        cls.docker = DockerClient()
        cls.docker.compose.down(volumes=True)
        cls.docker.compose.up(detach=True, wait=True)

    @classmethod
    def setUpClass(cls):
        cls.startDocker()
        cls.app = create_app().test_client()
        cls.project_name_1: str = "Project name 1"
        cls.project_name_2: str = "Project name 2"

    @classmethod
    def tearDownClass(cls):
        cls.docker.compose.down(volumes=True)

    def tearDown(self):
        self._delete_all_projects()

    def _delete_all_projects(self):
        response = self.app.get("/projects")
        projects_dict = json.loads(response.data)
        for project in projects_dict:
            self.app.delete(f"/projects/{project['id']['code']}")

    def test_get_all_projects(self):
        self.app.post("/projects", json={"name": self.project_name_1})
        self.app.post("/projects", json={"name": self.project_name_2})
        response = self.app.get("/projects")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(json.loads(response.data)))
        all_projects: Set[Project] = set(
            [deserialize(project, Project) for project in json.loads(response.data)]
        )
        self.assertEqual(
            frozenset(map(lambda p: p.name, all_projects)),
            {self.project_name_1, self.project_name_2},
        )

    def test_get_project(self):
        response = self.app.post("/projects", json={"name": self.project_name_1})
        project_id: ProjectId = deserialize(json.loads(response.data), ProjectId)
        response = self.app.get(f"/projects/{project_id.code}")
        self.assertEqual(response.status_code, 200)
        project: Project = deserialize(json.loads(response.data), Project)
        self.assertEqual(self.project_name_1, project.name)

    def test_get_non_existent_project(self):
        response = self.app.get("/projects/does-not-exist")
        self.assertEqual(response.status_code, 404)

    def test_insert_project(self):
        response = self.app.post("/projects", json={"name": self.project_name_1})
        self.assertEqual(response.status_code, 201)
        project_id: ProjectId = deserialize(json.loads(response.data), ProjectId)
        response = self.app.get(f"/projects/{project_id.code}")
        self.assertEqual(response.status_code, 200)
        project: Project = deserialize(json.loads(response.data), Project)
        self.assertEqual(
            self.project_name_1,
            project.name,
        )

    def test_update_project(self):
        response = self.app.post("/projects", json={"name": self.project_name_1})
        project_id: ProjectId = deserialize(json.loads(response.data), ProjectId)
        project_response = self.app.get(f"/projects/{project_id.code}")
        project: Project = deserialize(json.loads(project_response.data), Project)
        updated_project: Project = project.model_copy().add_to_context("key", "value")
        updated_project.name = "Updated project name"
        response = self.app.put(
            f"/projects/{project_id.code}",
            json=serialize(updated_project),
        )
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f"/projects/{project_id.code}")
        expected_project: Project = deserialize(json.loads(response.data), Project)
        self.assertEqual(updated_project.context, expected_project.context)


    def test_delete_project(self):
        response = self.app.post("/projects", json={"name": self.project_name_1})
        project_id: ProjectId = deserialize(json.loads(response.data), ProjectId)
        response = self.app.delete(f"/projects/{project_id.code}")
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f"/projects/{project_id.code}")
        self.assertEqual(response.status_code, 404)

    def test_delete_non_existent_project(self):
        response = self.app.delete("/projects/does-not-exist")
        self.assertEqual(response.status_code, 404)

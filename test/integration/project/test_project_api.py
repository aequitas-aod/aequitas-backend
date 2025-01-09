import json
from typing import Set

from domain.common.core import EntityId
from domain.project.core import Project
from presentation.presentation import deserialize, serialize
from test.integration.project import ProjectRelatedTestCase


class TestProjectsAPI(ProjectRelatedTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_name_1: str = "Project name 1"
        cls.project_name_2: str = "Project name 2"

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
        project_id: EntityId = self._create_project(self.project_name_1)
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
        project_id: EntityId = deserialize(json.loads(response.data), EntityId)
        response = self.app.get(f"/projects/{project_id.code}")
        self.assertEqual(response.status_code, 200)
        project: Project = deserialize(json.loads(response.data), Project)
        self.assertEqual(
            self.project_name_1,
            project.name,
        )

    def test_update_project(self):
        project_id: EntityId = self._create_project(self.project_name_1)
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

    def test_update_project_context(self):
        project_id: EntityId = self._create_project(self.project_name_1)
        project_response = self.app.get(f"/projects/{project_id.code}")
        project: Project = deserialize(json.loads(project_response.data), Project)
        expected_project: Project = project.model_copy().add_to_context(
            "key", json.dumps("value")
        )
        response = self.app.put(
            f"/projects/{project_id.code}/context?key=key",
            json="value",
        )
        self.assertEqual(response.status_code, 200)
        updated_project_response = self.app.get(f"/projects/{project_id.code}")
        updated_project: Project = deserialize(
            json.loads(updated_project_response.data), Project
        )
        self.assertEqual(expected_project, updated_project)

    def test_delete_project(self):
        project_id: EntityId = self._create_project(self.project_name_1)
        response = self.app.delete(f"/projects/{project_id.code}")
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f"/projects/{project_id.code}")
        self.assertEqual(response.status_code, 404)

    def test_delete_non_existent_project(self):
        response = self.app.delete("/projects/does-not-exist")
        self.assertEqual(response.status_code, 404)

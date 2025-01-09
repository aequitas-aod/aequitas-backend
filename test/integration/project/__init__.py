import json
from utils.logs import logger

from domain.common.core import EntityId
from presentation.presentation import deserialize, serialize
from infrastructure.ws.main import create_app
from test.integration import DockerComposeBasedTestCase


class ProjectRelatedTestCase(DockerComposeBasedTestCase):
    projects_to_create = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app = create_app().test_client()

    def setUp(self):
        super().setUp()
        self.projects_by_name = dict()
        for project_name in self.projects_to_create:
            proj_id = self._create_project(project_name)
            self.projects_by_name[project_name] = proj_id
            logger.info(f"Created project {project_name} with id {proj_id}")

    def tearDown(self):
        super().tearDown()
        self._delete_all_projects()

    @classmethod
    def _create_project(cls, project_name: str) -> EntityId:
        response = cls.app.post("/projects", json={"name": project_name})
        return deserialize(json.loads(response.data), EntityId)

    @classmethod
    def _delete_all_projects(cls):
        response = cls.app.get("/projects")
        projects_dict = json.loads(response.data)
        for project in projects_dict:
            cls.app.delete(f"/projects/{project['id']['code']}")
            logger.info(
                f"Deleted project {project['name']} with id {project['id']['code']}"
            )

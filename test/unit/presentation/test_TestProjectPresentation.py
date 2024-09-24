import unittest

from domain.project.core import Project, ProjectId
from domain.project.factories import ProjectFactory
from presentation.presentation import serialize, deserialize


class TestProjectPresentation(unittest.TestCase):

    def setUp(self):
        self.project: Project = ProjectFactory.create_project(
            ProjectId(code="project1"),
            "project_name",
            {"key": "value"},
        )
        self.project_dict: dict = {
            "id": {"code": "project1"},
            "name": "project_name",
            "context": {"key": "value"},
        }

    def test_serialize_question(self):
        expected: dict = {
            "id": {"code": "project1"},
            "name": "project_name",
            "context": {"key": "value"},
        }
        actual: dict = serialize(self.project)
        self.assertEqual(
            expected,
            actual,
        )

    def test_deserialize_project(self):
        expected: Project = ProjectFactory.create_project(
            ProjectId(code="project1"),
            "project_name",
            {"key": "value"},
        )
        actual: Project = deserialize(self.project_dict, Project)
        self.assertEqual(
            expected,
            actual,
        )

import unittest

from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.factories import ProjectFactory


class TestProjectContext(unittest.TestCase):

    def setUp(self):
        self.project_id: EntityId = ProjectFactory.id_of(code="project_id")
        self.project: Project = Project(
            id=self.project_id, name="Project name", context={}
        )

    def test_add_to_context(self):
        p = self.project.add_to_context("key", "value")
        self.assertEqual(p.context["key"], "value")

    def test_remove_from_context(self):
        p1 = self.project.add_to_context("key", "value")
        p2 = p1.remove_from_context("key")
        self.assertEqual(p2.context, {})

    def test_add_same_key_to_context_twice(self):
        p1 = self.project.add_to_context("key1", "value")
        self.assertRaises(
            ValueError,
            lambda: p1.add_to_context("key1", "value"),
        )

    def test_remove_non_existing_key_from_context(self):
        self.assertRaises(
            ValueError,
            lambda: self.project.remove_from_context("key"),
        )
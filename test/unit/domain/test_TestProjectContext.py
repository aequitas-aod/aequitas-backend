import unittest

from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.factories import ProjectFactory
from utils.encodings import encode


class TestProjectContext(unittest.TestCase):

    def setUp(self):
        self.project_id: EntityId = ProjectFactory.id_of(code="project_id")
        self.project: Project = Project(
            id=self.project_id, name="Project name", context={}
        )

    def test_get_context(self):
        p = self.project.add_to_context("key", "value").add_to_context("key2", "value2")
        self.assertEqual(p.context, {"key": encode("value"), "key2": encode("value2")})
        self.assertEqual(p.get_context(), {"key": "value", "key2": "value2"})

    def test_add_to_context(self):
        p = self.project.add_to_context("key", "value")
        self.assertEqual(p.context["key"], encode("value"))
        self.assertEqual(p.get_from_context("key"), b"value")

    def test_remove_from_context(self):
        p1 = self.project.add_to_context("key", "value")
        p2 = p1.remove_from_context("key")
        self.assertEqual(p2.context, {})

    def test_override_key_value(self):
        p1 = self.project.add_to_context("key", "value")
        p2 = p1.add_to_context("key", "different value")
        self.assertEqual(p2.context["key"], encode("different value"))

    def test_remove_non_existing_key_from_context(self):
        self.assertRaises(
            ValueError,
            lambda: self.project.remove_from_context("key"),
        )

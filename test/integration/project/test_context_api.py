import json

from test.integration.project import ProjectRelatedTestCase


class TestContextAPI(ProjectRelatedTestCase):
    projects_to_create = ["Project name 1"]

    def setUp(self):
        super().setUp()
        self.project_id = self.projects_by_name["Project name 1"]
        self.key = "k"
        self.value = {
            "key1": 1,
            "key2": "value2",
            "key3": [1, 2, 3],
            "key4": {"key5": "value5"},
            "key6": None,
            "key7": True,
        }

    def test_put_key(self):
        response = self.app.put(f"/projects/{self.project_id.code}/context?key={self.key}", json=self.value)
        self.assertEqual(response.status_code, 200)

    def test_get_missing_key(self):
        response = self.app.get(f"/projects/{self.project_id.code}/context?key={self.key}")
        self.assertEqual(response.status_code, 404)

    def test_get_key(self):
        self.app.put(f"/projects/{self.project_id.code}/context?key={self.key}", json=self.value)
        response = self.app.get(f"/projects/{self.project_id.code}/context?key={self.key}")
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(response, self.value)

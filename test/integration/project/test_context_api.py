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
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key={self.key}", json=self.value
        )
        self.assertEqual(response.status_code, 200)

    def test_get_missing_key(self):
        response = self.app.get(
            f"/projects/{self.project_id.code}/context?key={self.key}&wait=false"
        )
        self.assertEqual(response.status_code, 404)

    def test_get_missing_key_timout(self):
        response = self.app.get(
            f"/projects/{self.project_id.code}/context?key={self.key}&wait=True&timeout=0.5"
        )
        self.assertEqual(response.status_code, 408)

    def test_get_key(self):
        self.test_put_key()
        response = self.app.get(
            f"/projects/{self.project_id.code}/context?key={self.key}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("plain/text", response.headers["Content-Type"])
        response = json.loads(response.data)
        self.assertEqual(response, self.value)

    def test_get_all(self):
        self.test_put_key()
        self.app.get(f"/projects/{self.project_id.code}/context")
        response = self.app.get(f"/projects/{self.project_id.code}/context")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers["Content-Type"])
        self.assertIsInstance(response.json, dict)
        self.assertIn(self.key, response.json)
        self.assertIsInstance(response.json[self.key], str)
        self.assertEqual(json.loads(response.json[self.key]), self.value)

    def test_post_dataset(self):
        from resources.db.datasets import dataset_path
        from pandas import read_csv
        from io import BytesIO

        self.dataset_path = dataset_path("AdultDataset")
        self.dataset = read_csv(self.dataset_path)
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key=dataset__adult",
            data=self.dataset_path.read_bytes(),
            content_type="plain/text",
        )
        self.assertEqual(response.status_code, 200)
        response = self.app.get(
            f"/projects/{self.project_id.code}/context?key=dataset__adult"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("plain/text", response.headers["Content-Type"])
        raw_dataset = response.data
        dataset = read_csv(BytesIO(raw_dataset))
        self.assertTrue(self.dataset.equals(dataset))

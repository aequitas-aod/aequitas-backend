from io import BytesIO
from time import sleep

import pandas
from pandas import read_csv

import infrastructure.ws.setup
from test.integration.project import ProjectRelatedTestCase


class AutomationRelatedTestCase(ProjectRelatedTestCase):
    services = ["db", "kafka"]
    projects_to_create = ["Project name 1"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        infrastructure.ws.setup.enable_automation()

    def setUp(self):
        super().setUp()
        self.project_id = self.projects_by_name["Project name 1"]


class TestContextAutomation(AutomationRelatedTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from resources.db.datasets import dataset_path
        from pandas import read_csv

        cls.dataset_path = dataset_path("adult")
        cls.dataset = read_csv(cls.dataset_path)

    def setUp(self):
        super().setUp()
        self.dataset_id = "adult"

    def test_dataset_created_produces(self):
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key=dataset__{self.dataset_id}",
            data=self.dataset_path.read_bytes(),
            content_type="plain/text",
        )
        self.assertEqual(response.status_code, 200)
        sleep(10)  # FIXME: make GET suspensive on context
        for key_prefix in ["dataset_head", "stats"]:
            key = f"{key_prefix}__{self.dataset_id}"
            with self.subTest(key=key):
                response = self.app.get(
                    f"/projects/{self.project_id.code}/context?key={key}"
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("plain/text", response.headers["Content-Type"])
                raw_dataset = response.data
                dataset = read_csv(BytesIO(raw_dataset))
                self.assertIsInstance(dataset, pandas.DataFrame)
                self.assertTrue(len(dataset) > 0)

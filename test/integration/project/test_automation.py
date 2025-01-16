from io import BytesIO
import json
import pandas as pd
from application.automation.parsing import read_csv, parse_json
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # TODO docker compose down kafka (and only kafka)
        # TODO disable automation scripts and shut down the ones who are running (to be implemented)


class TestContextAutomation(AutomationRelatedTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from resources.db.datasets import dataset_path
        from test.resources.adult import PATH_FEATURES_JSON

        cls.dataset_path = dataset_path("adult")
        cls.dataset = read_csv(cls.dataset_path)
        cls.features = json.loads(PATH_FEATURES_JSON.read_text())

    def setUp(self):
        super().setUp()
        self.dataset_id = "adult"
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key=dataset__{self.dataset_id}",
            data=self.dataset_path.read_bytes(),
            content_type="plain/text",
        )
        self.assertResponseIsSuccessful(response)

    def test_dataset_created_produces(self):
        for key_prefix in ["dataset_head", "stats"]:
            key = f"{key_prefix}__{self.dataset_id}"
            with self.subTest(key=key):
                response = self.app.get(
                    f"/projects/{self.project_id.code}/context?key={key}"
                )
                self.assertResponseIsSuccessful(response)
                self.assertIn("plain/text", response.headers["Content-Type"])
                self.assertIsNonEmptyDataFrameInCsvFormat(response.data)

    def assertIsNonEmptyDataFrameInCsvFormat(self, data: bytes):
        dataset = read_csv(BytesIO(data))
        self.assertIsInstance(dataset, pd.DataFrame)
        self.assertTrue(len(dataset) > 0)

    def asserIsSvg(self, data: bytes):
        self.assertTrue(
            data.startswith(b'<?xml version="1.0" encoding="utf-8" standalone="no"?>')
        )
        self.assertIn(b"</svg>", data)

    def assertIsJson(self, data: bytes):
        self.assertIsInstance(parse_json(data.decode("utf-8")), dict)

    def test_features_created_produces(self):
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key=features__{self.dataset_id}",
            json=self.features,
        )
        self.assertResponseIsSuccessful(response)
        key_results = {
            "actual_dataset": self.assertIsNonEmptyDataFrameInCsvFormat,
            "correlation_matrix": self.asserIsSvg,
            "suggested_proxies": self.assertIsJson,
            "metrics": self.assertIsJson,
        }
        for key_prefix, assertion in key_results.items():
            key = f"{key_prefix}__{self.dataset_id}"
            with self.subTest(key=key):
                response = self.app.get(
                    f"/projects/{self.project_id.code}/context?key={key}"
                )
                self.assertResponseIsSuccessful(response)
                self.assertIn("plain/text", response.headers["Content-Type"])
                assertion(response.data)

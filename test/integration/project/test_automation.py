import unittest
from io import BytesIO
import pandas as pd
from application.automation.parsing import read_csv, parse_json
import infrastructure.ws.setup
from test.integration.project import ProjectRelatedTestCase
from test.resources.adult import *


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

        cls.dataset_path = dataset_path("adult")
        cls.dataset = read_csv(cls.dataset_path)
        cls.features = json.loads(PATH_FEATURES_JSON.read_text())

    def setUp(self):
        super().setUp()
        self.dataset_id = "adult-1"
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key=dataset__{self.dataset_id}",
            data=self.dataset_path.read_bytes(),
            content_type="plain/text",
        )
        self.assertResponseIsSuccessful(response)

    def test_dataset_created_produces(self):
        for key_prefix in ["dataset_head", "stats"]:
            key = f"{key_prefix}__{self.dataset_id}"
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
        parsed = parse_json(data.decode("utf-8"))
        self.assertTrue(isinstance(parsed, dict) or isinstance(parsed, list))

    def test_features_created_produces(self):
        self.test_dataset_created_produces()
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
            response = self.app.get(
                f"/projects/{self.project_id.code}/context?key={key}"
            )
            self.assertResponseIsSuccessful(response)
            self.assertIn("plain/text", response.headers["Content-Type"])
            assertion(response.data)

    def _proxies_and_detected(self):
        key = f"proxies__{self.dataset_id}"
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key={key}",
            json=get_json(PATH_PROXIES_JSON),
        )
        self.assertResponseIsSuccessful(response)
        key = f"detected__{self.dataset_id}"
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key={key}",
            json=get_json(PATH_DETECTED_JSON),
        )
        self.assertResponseIsSuccessful(response)

    def assertCurrentDatasetIs(self, expected_id: str):
        key = "current_dataset"
        response = self.app.get(f"/projects/{self.project_id.code}/context?key={key}")
        self.assertResponseIsSuccessful(response)
        self.assertIn("plain/text", response.headers["Content-Type"])
        self.assertEqual(response.data.decode("utf-8"), expected_id)

    def assertLastProcessingIs(self, phase: str, algorithm: str, dataset: str):
        key = "processing_history"
        response = self.app.get(f"/projects/{self.project_id.code}/context?key={key}")
        self.assertResponseIsSuccessful(response)
        self.assertIn("plain/text", response.headers["Content-Type"])
        parsed = parse_json(response.data.decode("utf-8"))
        self.assertIsInstance(parsed, list)
        self.assertTrue(len(parsed) > 0)
        last_processing = parsed[-1]
        self.assertEqual(last_processing["phase"], phase)
        self.assertEqual(last_processing["dataset"], dataset)
        self.assertEqual(last_processing["algorithm"], algorithm)

    def test_preprocessing_requested_produces(self):
        self.test_features_created_produces()
        self._proxies_and_detected()
        request = get_json(PATH_PREPROCESSING_JSON)
        algorithm = request["$algorithm"]
        key = f"preprocessing__{self.dataset_id}"
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key={key}",
            json=request,
        )
        self.assertResponseIsSuccessful(response)
        key_results = {
            "correlation_matrix": self.asserIsSvg,
            "metrics": self.assertIsJson,
            "preprocessing_plot": self.asserIsSvg,
            "performance_plot": self.asserIsSvg,
            "fairness_plot": self.asserIsSvg,
            "dataset": self.assertIsNonEmptyDataFrameInCsvFormat,
            "dataset_head": self.assertIsNonEmptyDataFrameInCsvFormat,
            "stats": self.assertIsNonEmptyDataFrameInCsvFormat,
        }
        result_id = "adult-2"
        for key_prefix, assertion in key_results.items():
            key = f"{key_prefix}__{result_id}"
            # with self.subTest(get=key):
            response = self.app.get(
                f"/projects/{self.project_id.code}/context?key={key}"
            )
            self.assertResponseIsSuccessful(response)
            self.assertIn("plain/text", response.headers["Content-Type"])
            assertion(response.data)
        self.assertCurrentDatasetIs(result_id)
        self.assertLastProcessingIs("pre", algorithm, self.dataset_id)

    def test_inprocessing_requested_produces(self):
        self.test_features_created_produces()
        self._proxies_and_detected()
        request = get_json(PATH_INPROCESSING_JSON)
        algorithm = request["$algorithm"]
        key = f"inprocessing__{self.dataset_id}"
        response = self.app.put(
            f"/projects/{self.project_id.code}/context?key={key}",
            json=request,
        )
        self.assertResponseIsSuccessful(response)
        key_results = {
            "predictions": self.assertIsNonEmptyDataFrameInCsvFormat,
            "correlation_matrix": self.asserIsSvg,
            "metrics": self.assertIsJson,
            "performance_plot": self.asserIsSvg,
            "fairness_plot": self.asserIsSvg,
            # "polarization_plot": self.asserIsSvg,
        }
        for key_prefix, assertion in key_results.items():
            key = f"{key_prefix}__{algorithm}__{self.dataset_id}"
            response = self.app.get(
                f"/projects/{self.project_id.code}/context?key={key}"
            )
            self.assertResponseIsSuccessful(response)
            self.assertIn("plain/text", response.headers["Content-Type"])
            assertion(response.data)
        self.assertLastProcessingIs("in", algorithm, self.dataset_id)

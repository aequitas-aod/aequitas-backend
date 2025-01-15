import unittest
import pandas as pd

from application.automation.parsing import to_csv, read_csv, to_json, read_json
from application.automation.scripts.on_dataset_created import get_stats
from application.automation.scripts.on_dataset_features_available import (
    generate_correlation_matrix_picture,
    generate_proxy_suggestions,
    compute_metrics,
)


class TestDatasetRelatedFunctionalities(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        import resources.db.datasets as datasets
        from test.resources.adult import PATH_FEATURES_JSON

        self.dataset = read_csv(datasets.dataset_path("adult"))
        self.features = read_json(PATH_FEATURES_JSON)
        assert isinstance(self.features, dict)
        self.sensitives = [
            f
            for f, opts in self.features.items()
            if "sensitive" in opts and opts["sensitive"]
        ]
        self.targets = [
            f
            for f, opts in self.features.items()
            if "target" in opts and opts["target"]
        ]
        self.drops = [
            f for f, opts in self.features.items() if "drop" in opts and opts["drop"]
        ]

    def assertDataFramesAreEqual(self, df1: pd.DataFrame, df2: pd.DataFrame):
        pd.testing.assert_frame_equal(df1, df2)

    def test_get_stats(self):
        with self.subTest("adult"):
            from test.resources.adult import PATH_STATS_CSV

            result = get_stats(self.dataset)
            expected = read_csv(PATH_STATS_CSV)
            self.assertDataFramesAreEqual(result, expected)
        with self.subTest("csv"):
            result_csv = to_csv(result)
            expected_csv = PATH_STATS_CSV.read_text()
            self.assertEqual(result_csv, expected_csv)

    def assertContainersAreAlmostEqual(self, value, other, tolerance: float = 1e-3):
        if isinstance(value, dict):
            self.assertIsInstance(other, dict)
            self.assertEqual(len(value), len(other))
            self.assertEqual(set(value.keys()), set(other.keys()))
            for k, v in value.items():
                self.assertContainersAreAlmostEqual(v, other[k], tolerance)
        elif isinstance(value, list):
            self.assertIsInstance(other, list)
            self.assertEqual(len(value), len(other))
            for i in range(len(value)):
                self.assertContainersAreAlmostEqual(value[i], other[i], tolerance)
        elif isinstance(value, float):
            self.assertAlmostEqual(value, other, delta=tolerance)
        else:
            self.assertEqual(value, other)

    def test_proxy_suggestions(self):
        from test.resources.adult import PATH_SUGGESTED_PROXIES_JSON

        result = generate_proxy_suggestions(self.dataset, self.sensitives, self.targets)
        expected = read_json(PATH_SUGGESTED_PROXIES_JSON)
        self.assertContainersAreAlmostEqual(result, expected)

    def test_correlation_matrix_picture(self):
        import io
        from test.resources.adult import PATH_CORRELATION_MATRIX_SVG

        actual_svg = io.StringIO()
        generate_correlation_matrix_picture(self.dataset, actual_svg)
        actual_svg = actual_svg.getvalue().splitlines()
        expected_svg = PATH_CORRELATION_MATRIX_SVG.read_text().splitlines()
        self.assertEqual(len(actual_svg), len(expected_svg))
        self.assertEqual(actual_svg[:4], expected_svg[:4])

    def test_compute_metrics(self):
        # TODO @josephgiovanelli implement this test, possibly changing the tolerance and the content of the metrics file
        from test.resources.adult import PATH_ACTUAL_DATASET_CSV, PATH_METRICS_JSON

        dataset = read_csv(PATH_ACTUAL_DATASET_CSV)
        actual = compute_metrics(dataset, self.sensitives, self.targets)
        expected = read_json(PATH_METRICS_JSON)
        self.assertContainersAreAlmostEqual(actual, expected, tolerance=2.0)

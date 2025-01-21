import unittest
import pandas as pd

from utils.logs import logger

from application.automation.parsing import to_csv, read_csv, to_json, read_json
from application.automation.scripts.on_dataset_created import get_stats
from application.automation.scripts.on_dataset_features_available import (
    generate_correlation_matrix_picture,
    generate_proxy_suggestions,
    compute_metrics,
)
from application.automation.scripts.on_processing_requested import (
    preprocessing_algorithm_CorrelationRemover,
    preprocessing_algorithm_LearnFairRepresentation,
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

    def assertDataFramesAreEqual(
        self, df1: pd.DataFrame, df2: pd.DataFrame, tolerance: float = None
    ):
        if tolerance is None:
            pd.testing.assert_frame_equal(df1, df2)
        else:
            pd.testing.assert_frame_equal(
                left=df1,
                right=df2,
                check_exact=False,
                atol=tolerance,
            )

    def assertDataFramesHaveSameStructure(self, df1: pd.DataFrame, df2: pd.DataFrame):
        self.assertEqual(df1.shape, df2.shape)
        self.assertEqual([str(c) for c in df1.columns], [str(c) for c in df2.columns])

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
        from test.resources.adult import PATH_ACTUAL_DATASET_CSV, PATH_METRICS_JSON

        dataset = read_csv(PATH_ACTUAL_DATASET_CSV)
        actual = compute_metrics(dataset, self.sensitives, self.targets)
        expected = read_json(PATH_METRICS_JSON)
        self.assertContainersAreAlmostEqual(actual, expected, tolerance=0.5)

    def __preprocessing_algorithm_LearnFairRepresentation(self):
        from resources.db.datasets import dataset_path
        from resources.db.context import context_data

        hyperparameters = context_data("preprocessing-hyperparameters")[
            "LearnFairRepresentation"
        ]
        hyperparameters = {k: hyperparameters[k]["default"] for k in hyperparameters}

        dataset = read_csv(dataset_path("adult"))
        result = preprocessing_algorithm_LearnFairRepresentation(
            dataset,
            sensitive=["native-country", "race", "sex", "workclass"],
            targets=["class"],
            **hyperparameters
        )
        return result

    def test_preprocessing_algorithm_LearnFairRepresentation(self):
        from test.resources.adult import PATH_PREPROCESSING_LFR_CSV

        result = self.__preprocessing_algorithm_LearnFairRepresentation()
        expected = read_csv(PATH_PREPROCESSING_LFR_CSV)
        self.assertDataFramesHaveSameStructure(result, expected)

    def test_metrics_after_LFR(self):
        result = self.__preprocessing_algorithm_LearnFairRepresentation()
        compute_metrics(
            result,
            sensitives=["native-country", "race", "sex", "workclass"],
            targets=["class"],
        )
        # FIXME: @josephgiovanelli, this computation taks too much time.
        # I believe that the problem is a consequence of the fact that LFR
        # outputs a dataset with numeric columns, so the computation of fairness metrics
        # has too many values to consider... is this intended?
        # If yes, then we should possibly discretize the result of LFR before computing the metrics.
        # If not, then there may be a bug in the implementation of LFR.

    def test_preprocessing_algorithm_CorrelationRemover(self):
        from resources.db.datasets import dataset_path

        from test.resources.adult import PATH_PREPROCESSING_CR_CSV

        dataset = read_csv(dataset_path("adult"))
        my_conf = {"alpha": 0.5}
        result = preprocessing_algorithm_CorrelationRemover(
            dataset, ["sex"], ["class"], **my_conf
        )
        expected = read_csv(PATH_PREPROCESSING_CR_CSV)

        self.assertDataFramesAreEqual(result, expected)


if __name__ == "__main__":
    unittest.main()

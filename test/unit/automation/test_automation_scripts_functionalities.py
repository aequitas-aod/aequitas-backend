import unittest
import pandas as pd

from application.automation.parsing import to_csv, read_csv, read_json
from application.automation.scripts.on_dataset_created import get_stats
from application.automation.scripts.on_dataset_features_available import (
    generate_correlation_matrix_picture,
    generate_proxy_suggestions,
    compute_metrics,
)
from application.automation.scripts.on_processing_requested import (
    generate_plot_picture,
    inprocessing_algorithm_FaUCI,
    inprocessing_algorithm_no_mitigation,
    preprocessing_algorithm_CorrelationRemover,
    preprocessing_algorithm_LearnedFairRepresentations,
)

from test.resources.adult import *


class TestDatasetRelatedFunctionalities(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        import resources.db.datasets as datasets

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
        result = generate_proxy_suggestions(self.dataset, self.sensitives, self.targets)
        expected = read_json(PATH_SUGGESTED_PROXIES_JSON)
        self.assertContainersAreAlmostEqual(result, expected)

    def test_correlation_matrix_picture(self):
        import io

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

    def __preprocessing_algorithm_LearnedFairRepresentations(self):
        from resources.db.datasets import dataset_path
        from resources.db.context import context_data

        hyperparameters = context_data("preprocessing-hyperparameters")[
            "LearnedFairRepresentations"
        ]
        hyperparameters = {k: hyperparameters[k]["default"] for k in hyperparameters}

        dataset = read_csv(dataset_path("adult"))
        result = preprocessing_algorithm_LearnedFairRepresentations(
            dataset, sensitive=["sex"], targets=["class"], **hyperparameters
        )
        return result

    def test_preprocessing_algorithm_LearnedFairRepresentations(self):
        result = self.__preprocessing_algorithm_LearnedFairRepresentations()
        expected = read_csv(PATH_PREPROCESSING_LFR_CSV)
        self.assertDataFramesHaveSameStructure(result, expected)

    def test_metrics_after_LFR(self):
        result = self.__preprocessing_algorithm_LearnedFairRepresentations()
        compute_metrics(
            result,
            sensitives=["sex"],
            targets=["class"],
        )

    def test_preprocessing_algorithm_CorrelationRemover(self):
        from resources.db.datasets import dataset_path

        dataset = read_csv(dataset_path("adult"))
        my_conf = {"alpha": 0.5}
        result = preprocessing_algorithm_CorrelationRemover(
            dataset, ["sex"], ["class"], **my_conf
        )
        expected = read_csv(PATH_PREPROCESSING_CR_CSV)

        self.assertDataFramesAreEqual(result, expected)

    def test_inprocessing_algorithm_FaUCI(self):
        from resources.db.datasets import dataset_path
        from resources.db.context import context_data

        dataset = read_csv(dataset_path("adult"))
        hyperparameters = context_data("inprocessing-hyperparameters")["FaUCI"]

        hyperparameters = {k: hyperparameters[k]["default"] for k in hyperparameters}

        (actual_predictions, actual_results) = inprocessing_algorithm_FaUCI(
            dataset, ["sex"], ["class"], **hyperparameters
        )

        # alpha = 0.5
        expected_predictions = read_csv(PATH_INPROCESSING_FAUCI_PRED_CSV)
        self.assertDataFramesAreEqual(actual_predictions, expected_predictions)

        # actual_results.to_csv(PATH_INPROCESSING_FAUCI_RES_CSV, index=False)
        expected_results = read_csv(PATH_INPROCESSING_FAUCI_RES_CSV)
        self.assertDataFramesAreEqual(actual_results, expected_results, tolerance=0.2)

        # alpha = 0
        hyperparameters["lambda"] = 0
        (actual_predictions, actual_results) = inprocessing_algorithm_FaUCI(
            dataset, ["sex"], ["class"], **hyperparameters
        )
        expected_predictions = read_csv(PATH_INPROCESSING_FAUCI_PRED_CSV)
        self.assertDataFramesAreEqual(actual_predictions, expected_predictions)

        # actual_results.to_csv(PATH_INPROCESSING_FAUCI_RES_0_CSV, index=False)
        expected_results = read_csv(PATH_INPROCESSING_FAUCI_RES_0_CSV)
        self.assertDataFramesAreEqual(actual_results, expected_results, tolerance=0.2)

        # alpha = 1
        hyperparameters["lambda"] = 1
        (actual_predictions, actual_results) = inprocessing_algorithm_FaUCI(
            dataset, ["sex"], ["class"], **hyperparameters
        )
        expected_predictions = read_csv(PATH_INPROCESSING_FAUCI_PRED_CSV)
        self.assertDataFramesAreEqual(actual_predictions, expected_predictions)

        # actual_results.to_csv(PATH_INPROCESSING_FAUCI_RES_1_CSV, index=False)
        expected_results = read_csv(PATH_INPROCESSING_FAUCI_RES_1_CSV)
        self.assertDataFramesAreEqual(actual_results, expected_results, tolerance=0.2)

    def test_inprocessing_pictures(self):
        import io

        get_result_file = lambda l: (
            PATH_INPROCESSING_FAUCI_RES_0_CSV
            if l == 0
            else (
                PATH_INPROCESSING_FAUCI_RES_1_CSV
                if l == 1
                else PATH_INPROCESSING_FAUCI_RES_CSV
            )
        )
        get_performance_file = lambda l: (
            PATH_INPROCESSING_PERFORMANCE_0_SVG
            if l == 0
            else (
                PATH_INPROCESSING_PERFORMANCE_1_SVG
                if l == 1
                else PATH_INPROCESSING_PERFORMANCE_SVG
            )
        )
        get_fairness_file = lambda l: (
            PATH_INPROCESSING_FAIRNESS_0_SVG
            if l == 0
            else (
                PATH_INPROCESSING_FAIRNESS_1_SVG
                if l == 1
                else PATH_INPROCESSING_FAIRNESS_SVG
            )
        )
        get_polarization_file = lambda l: (
            PATH_INPROCESSING_POLARIZATION_0_SVG
            if l == 0
            else (
                PATH_INPROCESSING_POLARIZATION_1_SVG
                if l == 1
                else PATH_INPROCESSING_POLARIZATION_SVG
            )
        )

        for l in [0, 0.5, 1]:
            for plot_type, file_name in {
                "performance": get_performance_file(l),
                "fairness": get_fairness_file(l),
                "polarization": get_polarization_file(l),
            }.items():
                results = read_csv(get_result_file(l))
                actual_svg = io.StringIO()
                generate_plot_picture(
                    plot_type=plot_type, results=results, file=file_name
                )
                # actual_svg = actual_svg.getvalue().splitlines()
                # expected_svg = file_name.read_text().splitlines()
                # self.assertEqual(len(actual_svg), len(expected_svg))
                # self.assertEqual(actual_svg[:4], expected_svg[:4])

    def test_inprocessing_algorithm_no_mitigation(self):
        from resources.db.datasets import dataset_path

        dataset = read_csv(dataset_path("adult"))
        actual_results = inprocessing_algorithm_no_mitigation(
            dataset, ["sex"], ["class"]
        )
        # actual_results.to_csv(PATH_INPROCESSING_NO_MIT_CSV, index=False)
        expected_results = read_csv(PATH_INPROCESSING_NO_MIT_CSV)
        self.assertDataFramesAreEqual(actual_results, expected_results, tolerance=0.2)

        # for plot_type, file_name in {
        #     "performance": DIR / "my_test_performance.svg",
        #     "fairness": DIR / "my_test_fairness.svg",
        #     "polarization": DIR / "my_test_polarization.svg",
        # }.items():
        #     generate_plot_picture(
        #         plot_type=plot_type, results=actual_results, file=file_name
        #     )

    def test_preprocessing_picture(self):
        import io
        from resources.db.datasets import dataset_path

        dataset = read_csv(dataset_path("adult"))
        transformed_df = read_csv(PATH_PREPROCESSING_LFR_CSV)

        actual_svg = io.StringIO()
        generate_plot_picture(
            plot_type="pre-processing",
            results=transformed_df,
            file=actual_svg,
            **{"original_dataset": dataset, "class_feature": "class"},
        )
        actual_svg = actual_svg.getvalue().splitlines()
        expected_svg = PATH_PREPROCESSING_SVG.read_text().splitlines()
        self.assertEqual(len(actual_svg), len(expected_svg))
        self.assertEqual(actual_svg[:4], expected_svg[:4])


if __name__ == "__main__":
    unittest.main()

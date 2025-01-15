import unittest
import pandas as pd

from application.automation.parsing import to_csv, read_csv
from application.automation.scripts.on_dataset_created import get_stats
from application.automation.scripts.on_dataset_features_available import (
    discretize_columns,
    generate_correlation_matrix_picture,
    generate_proxy_suggestions,
)


class TestDatasetRelatedFunctionalities(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        import resources.db.datasets as datasets

        self.dataset = read_csv(datasets.dataset_path("adult"))

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

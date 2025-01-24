import unittest
import pandas as pd
from application.automation.parsing import read_csv
from application.automation.scripts.on_dataset_features_available import (
    _discretize_numerical_columns,
)
from resources.db.datasets import dataset_path
from test.resources.adult import *


PATH_ADULT = dataset_path("adult")


class TestDataframeFunctionalities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = read_csv(PATH_ADULT)

    def test_discretize_numerical_columns(self):
        _discretize_numerical_columns(self.df)

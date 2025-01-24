import io
import json
from typing import Iterable, Union
import functools

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.preprocessing import OrdinalEncoder, KBinsDiscretizer

import utils.env
from utils.logs import logger
from application.automation.parsing import to_csv, _pythonize
from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import set_other_loggers_level

from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric

matplotlib.use("agg")
THRESHOLD_PROXY = 0.8

FIG_WIDTH_SIZE = 12
FIG_HEIGHT_SIZE = 10
FIG_MAX_FEATS = 25
FIG_MIN_CORR = -1
FIG_MAX_CORR = 1
FIG_DPI = 300

# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()


class AbstractDatasetFeaturesAvailableReaction(Automator):
    def __init__(self):
        super().__init__(["features.created"])

    @staticmethod
    def check_dataset_and_features(
        context_key: str, features: object, dataset_key: str, dataset: pd.DataFrame
    ):
        assert isinstance(
            features, dict
        ), f"Expected a dictionary, got {type(features)}"
        assert (x := set(features.keys())) == (y := set(dataset.columns)), (
            f"The features mentioned in {context_key} ({', '.join(x)}) "
            f"do not match the columns in {dataset_key} ({', '.join(y)})"
        )

    # noinspection PyMethodOverriding
    def on_event(
        self, topic: str, project_id: EntityId, project: Project, context_key: str
    ):
        dataset_id: str = context_key.split("__")[1]
        dataset_key: str = f"dataset__{dataset_id}"
        dataset: pd.DataFrame = self.get_from_context(project_id, dataset_key, "csv")
        features: dict = self.get_from_context(project_id, context_key, "json")
        self.check_dataset_and_features(context_key, features, dataset_key, dataset)
        targets = [key for key, value in features.items() if value["target"]]
        sensitive = [key for key, value in features.items() if value["sensitive"]]
        drops = [key for key, value in features.items() if value["drop"]]
        actual_dataset = dataset.drop(columns=drops, axis=1)
        for k, v in self.produce_info(dataset_id, actual_dataset, targets, sensitive):
            self.update_context(project_id, k, v)

    def produce_info(
        self,
        dataset_id: str,
        dataset: pd.DataFrame,
        targets: list[str],
        sensitive: list[str],
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        raise NotImplementedError("Subclasses must implement this method")


def _encode_categorical_columns(df: pd.DataFrame) -> pd.DataFrame:
    encoded_df = df.copy()
    categorical_features = encoded_df.select_dtypes(
        include=["object", "category"]
    ).columns

    # Apply Ordinal Encoding
    encoder = OrdinalEncoder()
    encoded_df[categorical_features] = encoder.fit_transform(
        encoded_df[categorical_features]
    )
    return encoded_df


def _needs_discretization(df: pd.DataFrame, features=None) -> bool:
    if not features:
        features = df.columns
    features = set(features)
    return any(
        pd.api.types.is_float_dtype(df[col]) for col in df.columns if col in features
    )


def _discretize_numerical_columns(df: pd.DataFrame, features=None) -> pd.DataFrame:
    if not features:
        features = list(df.columns)
    categorical_features = [
        col for col in features if pd.api.types.is_float_dtype(df[col])
    ]

    encoded_df = df.copy()

    for feature in categorical_features:
        logger.debug("Discretizing feature %s", feature)
        discretizer = KBinsDiscretizer(encode="ordinal", strategy="quantile")
        column = encoded_df[feature].values
        if column.ndim == 1:
            column = column.reshape(-1, 1)
        discretized = discretizer.fit_transform(column)
        encoded_df[feature] = discretized

    return encoded_df


def generate_correlation_matrix_picture(dataset: pd.DataFrame, file: io.IOBase):
    plt.figure(figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE))
    encoded_df = _encode_categorical_columns(dataset)
    ax = sns.heatmap(
        encoded_df.corr(),
        annot=len(encoded_df.columns) < FIG_MAX_FEATS,
        cmap="coolwarm",
        fmt=".2f",
    )
    ax.collections[0].set_clim(FIG_MIN_CORR, FIG_MAX_CORR)
    plt.title("Correlation Matrix Heatmap")
    plt.gcf().savefig(file, format="svg", dpi=FIG_DPI)


def generate_proxy_suggestions(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str]
) -> dict:
    result = dict()
    encoded_df = _encode_categorical_columns(
        dataset[[feature for feature in dataset.columns if feature not in targets]]
    )
    for sensitive_feature in sensitive:
        result[sensitive_feature] = dict()
        for feature in [f for f in encoded_df.columns if f != sensitive_feature]:
            correlation = encoded_df[sensitive_feature].corr(encoded_df[feature])
            suggested_proxy = abs(correlation) >= THRESHOLD_PROXY
            result[sensitive_feature][feature] = {
                "correlation": correlation if not np.isnan(correlation) else "?",
                "suggested_proxy": bool(suggested_proxy),
            }
    return result


THRESHOLD_CONTINOUS = 100
DEFAULT_METRICS = {"DisparateImpact", "StatisticalParityDifference"}


def compute_metrics(
    dataset: pd.DataFrame,
    sensitives: list[str],
    targets: list[str],
    metrics: list[str] = None,
) -> dict:
    if not metrics:
        metrics = set(DEFAULT_METRICS)
    else:
        metrics = set(metrics) & DEFAULT_METRICS

    relevant_columns = set(sensitives) | set(targets)
    if _needs_discretization(dataset, relevant_columns):
        dataset = _discretize_numerical_columns(dataset, relevant_columns)

    @functools.lru_cache(len(dataset.columns))
    def domain(feature):
        return sorted(dataset[feature].unique())

    result = {m: [] for m in metrics}

    for sensitive in sensitives:
        sensitive_domain = domain(sensitive)
        if len(sensitive_domain) > THRESHOLD_CONTINOUS:
            raise ValueError(f"Too many values for sensitive feature: {sensitive}")
        for sensitive_value in sensitive_domain:
            for target in targets:
                target_domain = domain(target)
                if len(target_domain) > THRESHOLD_CONTINOUS:
                    raise ValueError(f"Too many values for target feature: {target}")
                for target_value in target_domain:
                    logger.debug(
                        "Computing metrics for %s=%s and %s=%s",
                        sensitive,
                        sensitive_value,
                        target,
                        target_value,
                    )

                    df = dataset[[sensitive, target]]

                    for col, val in {
                        sensitive: sensitive_value,
                        target: target_value,
                    }.items():
                        if pd.api.types.is_integer_dtype(df[col]):
                            df.loc[:, col] = df[col].astype(str)
                        val_to_set = 1 if col == target else 0
                        df.loc[:, col] = df[col].apply(
                            lambda x: val_to_set if x == val else int(not (val_to_set))
                        )

                    bld = BinaryLabelDataset(
                        df=df,
                        label_names=[target],
                        protected_attribute_names=[sensitive],
                        favorable_label=1,
                        unfavorable_label=0,
                    )

                    unprivileged_groups = [{sensitive: 0}]
                    privileged_groups = [{sensitive: 1}]

                    metric = BinaryLabelDatasetMetric(
                        bld,
                        unprivileged_groups=unprivileged_groups,
                        privileged_groups=privileged_groups,
                    )

                    when_clause = {sensitive: sensitive_value, target: target_value}

                    if "DisparateImpact" in metrics:
                        disparate_impact = metric.disparate_impact()
                        result["DisparateImpact"].append(
                            {
                                "when": when_clause,
                                "value": _pythonize(disparate_impact),
                            }
                        )

                    if "StatisticalParityDifference" in metrics:
                        stat_parity_diff = metric.mean_difference()
                        result["StatisticalParityDifference"].append(
                            {
                                "when": when_clause,
                                "value": _pythonize(stat_parity_diff),
                            }
                        )

    return result


def correlation_matrix_picture(dataset: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    generate_correlation_matrix_picture(dataset, buffer)
    return buffer.getvalue()


def proxy_suggestions(
    dataset: pd.DataFrame, sensitive: list[str], targets: list[str]
) -> str:
    return json.dumps(generate_proxy_suggestions(dataset, sensitive, targets))


def metrics(
    dataset: pd.DataFrame,
    sensitive: list[str],
    targets: list[str],
    metrics: list[str] = None,
) -> str:
    return json.dumps(compute_metrics(dataset, sensitive, targets, metrics))


class ProxyDetectionReaction(AbstractDatasetFeaturesAvailableReaction):

    def produce_info(
        self,
        dataset_id: str,
        dataset: pd.DataFrame,
        targets: list[str],
        sensitive: list[str],
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        cases = [
            (f"actual_dataset__{dataset_id}", lambda: to_csv(dataset)),
            (
                f"correlation_matrix__{dataset_id}",
                lambda: correlation_matrix_picture(dataset),
            ),
            (
                f"suggested_proxies__{dataset_id}",
                lambda: proxy_suggestions(dataset, sensitive, targets),
            ),
            (f"metrics__{dataset_id}", lambda: metrics(dataset, sensitive, targets)),
        ]
        for k, v in cases:
            try:
                yield k, v()
            except Exception as e:
                self.log_error("Failed to produce %s", k, error=e)

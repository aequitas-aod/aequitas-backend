import io
import pandas as pd
import numpy as np


from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from typing import Iterable


class AbstractDatasetCreationReaction(Automator):
    def __init__(self):
        super().__init__(["datasets.created"])

    # noinspection PyMethodOverriding
    def on_event(
        self, topic: str, project_id: EntityId, project: Project, context_key: str
    ) -> None:
        dataset_id: str = context_key.split("__")[1]
        if project is not None:
            dataset_csv: str = project.get_from_context(context_key)
            dataset: pd.DataFrame = pd.read_csv(io.StringIO(dataset_csv))
            for key, value in self.produce_info(dataset_id, dataset):
                updated_project: Project = project.add_to_context(key, value)
                # noinspection PyUnresolvedReferences
                self.components.project_service.update_project(
                    updated_project.id, updated_project
                )
                self.logger.error(
                    "Set key %s of project %s to value %s",
                    key,
                    updated_project.id,
                    value.replace("\n", "\\n"),
                )

    def produce_info(
        self, dataset_id: str, dataset: pd.DataFrame
    ) -> Iterable[tuple[str, str]]:
        raise NotImplementedError("Subclasses must implement this method")


WORDS_SENSITIVE = ("sex", "race", "gender")
WORDS_TARGETS = ("class", "target", "output", "outcome")
DEFAULT_DISCRETIZATION_BINS = 10
outcome_feature = "class"
dataset = "adult"


def get_stats(
    df: pd.DataFrame, discretization_bins: int = DEFAULT_DISCRETIZATION_BINS
) -> pd.DataFrame:

    def _maybe_target(name: str):
        name = name.lower().strip()
        return any(word in name for word in WORDS_TARGETS)

    def _maybe_sensitive(name: str):
        name = name.lower().strip()
        return any(word in name for word in WORDS_SENSITIVE)

    def _get_distribution(feature: str):
        distribution = {}
        if df[feature].dtype == "int" or df[feature].dtype == "float":
            # For numerical features, create equi-width bins (maximum of 10 bins)
            counts, bin_edges = np.histogram(df[feature], bins=discretization_bins)
            bin_labels = [
                f"{round(bin_edges[i], 2)} - {round(bin_edges[i + 1], 2)}"
                for i in range(len(bin_edges) - 1)
            ]
            distribution["keys"] = bin_labels
            distribution["values"] = counts
            # distribution = dict(zip(bin_labels, counts))
        else:
            # For categorical features, show the 9 most-frequent keys and group the rest as "Others"
            value_counts = df[feature].value_counts()
            top_values = value_counts.nlargest(discretization_bins - 1)
            others_count = value_counts.iloc[(discretization_bins - 1) :].sum()
            distribution["keys"], distribution["values"] = [
                *top_values.to_dict().keys()
            ], [*top_values.to_dict().values()]
            if others_count > 0:
                distribution["keys"] += ["Others"]
                distribution["values"] += [others_count]
        return distribution

    # Define a new function to get distinct values and feature type
    def _get_distinct_values(feature: str):
        # For non-float features, return the distinct values
        if df[feature].dtype != "float":
            distinct_values = df[feature].unique()
            # if np.issubdtype(distinct_values.dtype, np.number):
            return sorted(distinct_values)
            # return distinct_values.tolist()
        return None

    def _get_feature_type(feature: str):
        unique_values = df[feature].nunique()
        if unique_values == 2:
            return "binary"
        elif df[feature].dtype == "int":
            return "integer"
        elif df[feature].dtype == "float":
            return "float"
        else:
            return "categorical"

    features_view = pd.DataFrame(data={"feature": df.columns})

    features_view = features_view.merge(
        right=df.describe().T.reset_index(),
        how="left",
        left_on="feature",
        right_on="index",
    )
    features_view = features_view.drop("index", axis=1)
    features_view["count"] = 0
    features_view = features_view.rename(
        columns={
            "count": "missing_values",
            "25%": "1st_percentile",
            "50%": "2nd_percentile",
            "75%": "3rd_percentile",
        }
    )

    # Add the new columns to the features_view DataFrame
    features_view["values"] = features_view["feature"].apply(_get_distinct_values)
    features_view["type"] = features_view["feature"].apply(_get_feature_type)
    features_view["distribution"] = features_view["feature"].apply(_get_distribution)
    features_view["output"] = [_maybe_target(col) for col in df.columns]
    features_view["sensitive"] = [_maybe_sensitive(col) for col in df.columns]

    features_view = features_view[
        [
            "feature",
            "missing_values",
            "min",
            "max",
            "mean",
            "std",
            "1st_percentile",
            "2nd_percentile",
            "3rd_percentile",
            "type",
            "values",
            "distribution",
            "output",
            "sensitive",
        ]
    ]

    return features_view


class DatasetInfoCreator(AbstractDatasetCreationReaction):
    def produce_info(
        self, dataset_id: str, dataset: pd.DataFrame
    ) -> Iterable[tuple[str, str]]:
        yield f"heads__{dataset_id}", dataset.head(100).to_csv()
        yield f"stats__{dataset_id}", get_stats(dataset).to_csv()
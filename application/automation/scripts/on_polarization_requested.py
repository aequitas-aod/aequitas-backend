import warnings
from typing import Iterable, Union

import pandas as pd
from pandas import DataFrame

from application.automation.parsing import to_csv, to_json
from application.automation.scripts.on_dataset_features_available import (
    metrics as generate_metrics,
    correlation_matrix_picture,
)
from application.automation.scripts.on_processing_requested import (
    generate_plot,
)
from application.automation.setup import Automator, DatasetInfo
from domain.common.core import EntityId
from domain.project.core import Project
from resources.adecco import (
    PATH_ADECCO_INPROCESSING_ADVDEB_POL_PRED_1_CSV,
    PATH_ADECCO_INPROCESSING_ADVDEB_POL_PRED_0_CSV,
    PATH_ADECCO_INPROCESSING_ADVDEB_POL_PRED_2_CSV,
)
from resources.akkodis import (
    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_0_CSV,
    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_CSV,
    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_1_CSV,
)
from resources.db.datasets import dataset_path
from resources.skin_deseases import (
    PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_POL_PRED_CSV,
)


def compute_polarization(
    sensitive: list[str],
    targets: list[str],
    algorithm: str,
    hyperparameters: dict,
    test_dataset_id: str,
    test_dataset: DataFrame,
    original_dataset: DataFrame,
):
    if "cand_provenance_gender" in sensitive:
        if hyperparameters["lambda_adv"] == 0:
            pred_path = PATH_ADECCO_INPROCESSING_ADVDEB_POL_PRED_0_CSV
        elif hyperparameters["lambda_adv"] == 1:
            pred_path = PATH_ADECCO_INPROCESSING_ADVDEB_POL_PRED_1_CSV
        else:
            pred_path = PATH_ADECCO_INPROCESSING_ADVDEB_POL_PRED_2_CSV
    elif "Sensitive" in sensitive:
        if hyperparameters["lambda_adv"] == 0:
            pred_path = PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_0_CSV
        elif hyperparameters["lambda_adv"] == 1:
            pred_path = PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_1_CSV
        else:
            pred_path = PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_CSV
    elif "f_ESCS" in sensitive:
        pred_path = dataset_path("preprocessed_lfr_result_ull")
    elif "skin_color" in sensitive:
        pred_path = PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_POL_PRED_CSV
    else:
        pred_path = dataset_path("fauci_predictions")

    pred = pd.read_csv(pred_path)

    if "lambda" in hyperparameters:
        pred = pred.drop("class", axis=1).rename(columns={"predictions": "class"})

    # TODO: compute new polarization metrics
    result = DataFrame()

    return pred, result


class PolarizationRequestedReaction(Automator):
    def __init__(self):
        super().__init__(["polarization.requested"])

    # noinspection PyMethodOverriding
    def on_event(
        self,
        topic: str,
        project_id: EntityId,
        project: Project,
        context_key: str,
        # phase: str,
    ):
        args = self.get_from_context(project_id, context_key, "json")
        processing_history = (
            self.get_from_context(
                project_id, f"processing_history", "json", optional=True
            )
            or []
        )
        if not processing_history:
            raise Exception(
                "Processing history is empty: it makes no sense to proceed with polarization"
            )
        last_processing = processing_history[-1]
        algorithm = last_processing["algorithm"]
        original_dataset_id = last_processing["dataset"]
        hyperparameters = last_processing["hyperparameters"]
        dataset_info = self.get_dataset_info_from_context(
            project_id, context_key, original_dataset_id
        )
        self.log(
            "Requested polarization after algorithm %s for dataset %s with metrics=%s, sensitives=%s, targets=%s",
            algorithm,
            dataset_info.dataset_id,
            dataset_info.metrics,
            dataset_info.selected_sensitives,
            dataset_info.selected_targets,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for k, v in self.produce_info(
                project_id,
                dataset_info,
                original_dataset_id,
                algorithm,
                hyperparameters,
                **args,
            ):
                self.update_context(project_id, k, v)
        self.update_context(project_id, processing_history=to_json(processing_history))

    def produce_info(
        self,
        project_id: EntityId,
        test_dataset_info: DatasetInfo,
        original_dataset_id: str,
        algorithm: str,
        hyperparameters: dict,
        **kwargs,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        test_dataset_id = test_dataset_info.dataset_id
        original_dataset: DataFrame = self.get_from_context(
            project_id, "dataset__" + original_dataset_id, "csv"
        )
        test_predictions, computed_metrics = compute_polarization(
            test_dataset_info.sensitive,
            test_dataset_info.targets,
            algorithm,
            hyperparameters,
            test_dataset_id,
            test_dataset_info.dataset,
            original_dataset,
        )
        test_predictions_head = test_predictions.head(100)

        # TODO: to remove when polarization metrics computation is implemented
        computed_metrics = self.get_from_context(
            project_id, f"computed_metrics__{algorithm}__{original_dataset_id}", "csv"
        )
        cases = [
            (
                f"polarization_plot__{algorithm}__{test_dataset_id}",  # TODO: add incremental ids
                lambda: generate_plot("polarization", computed_metrics),
            ),
            (
                f"predictions_head__{algorithm}__{test_dataset_id}",
                lambda: to_csv(test_predictions_head),
            ),
            (
                f"predictions__{algorithm}__{test_dataset_id}",
                lambda: to_csv(test_predictions),
            ),
            (
                f"correlation_matrix__{algorithm}__{test_dataset_id}",
                lambda: correlation_matrix_picture(test_predictions),
            ),
            (
                f"metrics__{algorithm}__{test_dataset_id}",
                lambda: generate_metrics(
                    test_predictions,
                    test_dataset_info.sensitive,
                    test_dataset_info.targets,
                    test_dataset_info.metrics,
                ),
            ),
        ]
        for k, v in cases:
            try:
                yield k, v()
            except Exception as e:
                self.log_error("Failed to produce %s", k, error=e)

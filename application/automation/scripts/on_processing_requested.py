import copy
import io
import json
import random
import warnings
from typing import Iterable, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from aif360.algorithms.preprocessing import LFR
from aif360.datasets import BinaryLabelDataset
from fairlearn import metrics as fairlearn_metrics
from fairlearn.metrics import demographic_parity_ratio, equalized_odds_ratio
from fairlearn.preprocessing import CorrelationRemover
from fairlib import DataFrame as FairDataFrame
from fairlib.inprocessing import Fauci, AdversarialDebiasing, PrejudiceRemover
from pandas.plotting import parallel_coordinates
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import (
    accuracy_score,
    recall_score,
    precision_score,
    roc_auc_score,
    f1_score,
)
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OrdinalEncoder

import utils.env
from application.automation.parsing import read_csv, to_csv, to_json
from application.automation.scripts.on_dataset_created import (
    get_heads,
    get_stats,
)
from application.automation.scripts.on_dataset_features_available import (
    metrics as generate_metrics,
    correlation_matrix_picture,
    selected_metrics,
)
from application.automation.setup import Automator
from domain.common.core import EntityId
from domain.project.core import Project
from resources.adecco import (
    PATH_ADECCO_INPROCESSING_ADVDEB_PRED_1_CSV,
    PATH_ADECCO_INPROCESSING_ADVDEB_RES_0_CSV,
    PATH_ADECCO_INPROCESSING_ADVDEB_PRED_0_CSV,
    PATH_ADECCO_INPROCESSING_ADVDEB_PRED_2_CSV,
    PATH_ADECCO_INPROCESSING_ADVDEB_RES_1_CSV,
    PATH_ADECCO_INPROCESSING_ADVDEB_RES_2_CSV,
)
from resources.adult import (
    PATH_INPROCESSING_FAUCI_RES_CSV,
    PATH_INPROCESSING_FAUCI_RES_0_CSV,
    PATH_INPROCESSING_FAUCI_RES_1_CSV,
)
from resources.akkodis import (
    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_0_CSV,
    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_CSV,
    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_1_CSV,
    PATH_AKKODIS_INPROCESSING_ADVDEB_RES_0_CSV,
    PATH_AKKODIS_INPROCESSING_ADVDEB_RES_CSV,
    PATH_AKKODIS_INPROCESSING_ADVDEB_RES_1_CSV,
    PATH_AKKODIS_METRICS_FAUCI_ORIGINAL_JSON,
    PATH_AKKODIS_METRICS_BASELINE_ORIGINAL_JSON,
    PATH_AKKODIS_FAUCI_RES_1_CSV,
    PATH_AKKODIS_BASELINE_RES_1_CSV,
)
from resources.db.datasets import dataset_path
from resources.skin_deseases import (
    PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_RES_NONE_CSV,
    PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_RES_MIN_CSV,
    PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_RES_BALANCED_CSV,
    PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_PRED_NONE_CSV,
    PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_PRED_MIN_CSV,
    PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_PRED_BALANCED_CSV,
)
from resources.ull import (
    PATH_ULL_INPROCESSING_BASELINE_RES_POL_1_CSV,
    PATH_ULL_INPROCESSING_BASELINE_PRED_CSV,
    PATH_ULL_INPROCESSING_BEST_RES_POL_1_CSV,
    PATH_ULL_INPROCESSING_BEST_PRED_CSV,
    PATH_ULL_METRICS_BASELINE_JSON,
    PATH_ULL_METRICS_BEST_JSON,
)
from utils.logs import logger
from utils.logs import set_other_loggers_level

FIG_WIDTH_SIZE = 12
FIG_HEIGHT_SIZE = 5
FIG_DPI = 300
PREPROCESSING_SAMPLE_SIZE = 200

FIG_WIDTH_SIZE = 12
FIG_HEIGHT_SIZE = 5
FIG_DPI = 300


# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()


class AbstractProcessingRequestedReaction(Automator):
    def __init__(self, *phases):
        super().__init__(["processing.requested"])
        self.__supported_phases = set(phases)

    @property
    def supported_phases(self):
        return tuple(self.__supported_phases)

    # noinspection PyMethodOverriding
    def on_event(
        self,
        topic: str,
        project_id: EntityId,
        project: Project,
        context_key: str,
        phase: str,
    ):
        if phase not in self.__supported_phases:
            self.log(
                "Ignoring event %s, because it is related to phase %s and this automator only supports phases %s",
                topic,
                phase,
                self.__supported_phases,
            )
            return
        dataset_info = self.get_dataset_info_from_context(project_id, context_key)
        hyperparameters = self.get_from_context(project_id, context_key, "json")
        algorithm = hyperparameters["$algorithm"]
        self.log(
            "Requested %sprocessing with algorithm %s for dataset %s with metrics=%s, sensitives=%s, targets=%s",
            phase,
            algorithm,
            dataset_info.dataset_id,
            dataset_info.metrics,
            dataset_info.selected_sensitives,
            dataset_info.selected_targets,
        )
        hp = hyperparameters.copy()
        del hp["$algorithm"]
        processing_history = dict(
            phase=phase,
            dataset=dataset_info.dataset_id,
            algorithm=algorithm,
            hyperparameters=hp,
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for k, v in self.produce_info(
                phase,
                dataset_info.dataset_id,
                dataset_info.dataset,
                dataset_info.metrics,
                dataset_info.selected_targets,
                dataset_info.selected_sensitives,
                dataset_info.proxies,
                dataset_info.detected,
                hyperparameters,
            ):
                self.update_context(project_id, k, v)
        self.update_context(project_id, processing_history=to_json(processing_history))

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        metrics: list[str],
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def next_name(dataset_id: str) -> str:
        if "-" in dataset_id:
            last = dataset_id.split("-")[-1]
            try:
                index = int(last)
                return dataset_id[: -len(last)] + str(index + 1)
            except ValueError:
                pass
        return dataset_id + "-1"

    def _call_global_algorithm(
        self,
        dataset: pd.DataFrame,
        dataset_id: str,
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
        prefix: str = None,
    ):
        if prefix is None:
            prefix = self.supported_phases[0]
        algorithm = hyperparameters.pop("$algorithm")
        function_name = f"{prefix}processing_algorithm_{algorithm}"
        if function_name not in globals():
            raise KeyError("No such algorithm: %s" % algorithm)
        function = globals()[function_name]
        self.log(
            "Executing %s: \n"
            "\ton dataset of shape %s\n"
            "\twith sensitive attributes %s\n"
            "\tand targets %s\n"
            "\twith hyperparameters %s",
            algorithm,
            dataset.shape,
            sensitive,
            targets,
            hyperparameters,
        )
        result = function(
            dataset,
            dataset_id,
            sensitive,
            targets,
            proxies=proxies,
            detected=detected,
            **hyperparameters,
        )
        self.log(
            "Executed %s: result is of type %s",
            algorithm,
            type(result),
        )
        return algorithm, result


class AIF360PreprocWrapper(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        aif360_model,
        sensitive_feature,
    ):
        self.aif360_model = aif360_model

        self.sensitive_feature = sensitive_feature

        self.class_feature = "label"

        self.ordinal_encoder = None
        self.favorable_sens_group = None
        self.unfavorable_sens_group = None

    def _encode_features(self, df, fit):

        df_encoded = df.copy()

        # Encode class
        if self.class_feature not in df_encoded.columns:
            df_encoded[self.class_feature] = 0  # or any constant value

        # Encode sensitive feature
        if (
            self.sensitive_feature
            in df_encoded.select_dtypes(include=["object", "category"]).columns
        ):

            favorable_sens_group = (
                df_encoded[self.sensitive_feature].value_counts().index[0]
            )
            unfavorable_sens_group = (
                df_encoded[self.sensitive_feature].value_counts().index[1]
            )
            if fit:
                self.favorable_sens_group = favorable_sens_group
                self.unfavorable_sens_group = unfavorable_sens_group
            df_encoded[self.sensitive_feature] = df_encoded[
                self.sensitive_feature
            ].apply(lambda x: 1 if x == favorable_sens_group else 0)

        # Encode other columns
        categorical_cols = df_encoded.select_dtypes(
            include=["object", "category"]
        ).columns
        numeric_cols = df_encoded.select_dtypes(exclude=["object", "category"]).columns

        if fit:
            self.ordinal_encoder = OrdinalEncoder()
            self.ordinal_encoder.fit(df_encoded[categorical_cols])

        if len(categorical_cols) > 0:
            df_encoded[categorical_cols] = self.ordinal_encoder.transform(
                df_encoded[categorical_cols]
            )
        if len(numeric_cols) > 0:
            df_encoded[numeric_cols] = df_encoded[numeric_cols]

        # Check missing values
        # print(df_encoded.isna().sum())
        # df_encoded = df_encoded.set_index(self.sensitive_feature)
        # print(df_encoded.isna().sum())
        # print(df_encoded)

        return df_encoded

    def fit(self, X, y, **kwargs):
        if not self.sensitive_feature:
            raise ValueError("Protected attribute name must be specified.")

        df_encoded = self._encode_features(df=X.assign(label=y), fit=True)

        # print(df_encoded)
        dataset = BinaryLabelDataset(
            df=df_encoded,
            label_names=[self.class_feature],
            # sensitive_features=[self.sensitive_feature],
            protected_attribute_names=[self.sensitive_feature],
            favorable_label=1,
            unfavorable_label=0,
        )
        self.aif360_model = self.aif360_model.fit(dataset, **kwargs)
        return self

    def transform(self, X, y, decode=False):
        X_encoded = self._encode_features(df=X.assign(label=y), fit=False)
        dataset = BinaryLabelDataset(
            df=X_encoded,
            label_names=[self.class_feature],
            # sensitive_features=[self.sensitive_feature],
            protected_attribute_names=[self.sensitive_feature],
            favorable_label=1,
            unfavorable_label=0,
        )
        new_X = self.aif360_model.transform(dataset).convert_to_dataframe()[0]
        new_X[self.sensitive_feature] = (
            new_X[self.sensitive_feature].apply(
                lambda x: (
                    self.favorable_sens_group if x == 1 else self.unfavorable_sens_group
                )
            )
            if decode
            else new_X[self.sensitive_feature]
        )
        return new_X


# def _get_default_settings(sensitive: list[str], targets: list[str]) -> dict:

#     sensitive_feat = sensitive[0]
#     target_feat = targets[0]

#     if sensitive_feat == "f_ESCS":
#         favorable_sensitive_label = "OTHERS"
#         unfavorable_sensitive_label = "DISADVANTAGED"

#         favorable_class_label = "PASSING"
#         unfavorable_class_label = "AT RISK"
#     else:
#         favorable_sensitive_label = "Male"
#         unfavorable_sensitive_label = "Female"

#         favorable_class_label = ">50K"
#         unfavorable_class_label = "<=50K"

#     return {
#         # sensitive variables
#         "sensitive_feat": sensitive_feat,
#         "favorable_sensitive_label": favorable_sensitive_label,
#         "unfavorable_sensitive_label": unfavorable_sensitive_label,
#         # target variables
#         "target_feat": target_feat,
#         "favorable_class_label": favorable_class_label,
#         "unfavorable_class_label": unfavorable_class_label,
#         "predictions_feat": "predictions",
#     }


def _discretize_columns(df: pd.DataFrame) -> pd.DataFrame:
    encoded_df = copy.deepcopy(df)
    categorical_features = encoded_df.select_dtypes(
        include=["object", "category"]
    ).columns

    # Apply Ordinal Encoding
    encoder = OrdinalEncoder()
    encoded_df[categorical_features] = encoder.fit_transform(
        encoded_df[categorical_features]
    )
    return encoded_df


def _filter_keys(data: dict, *keys):
    keys = set(keys)
    return {k: v for k, v in data.items() if k in keys}


def preprocessing_algorithm_StableDiffusionBasedDataAugmentation(
    dataset: pd.DataFrame,
    dataset_id: str,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> pd.DataFrame:
    if "min" in kwargs["augmentation_criterion"]:
        result_paths = (
            PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_PRED_MIN_CSV,
            PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_RES_MIN_CSV,
        )
    elif "balanced" in kwargs["augmentation_criterion"]:
        result_paths = (
            PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_PRED_BALANCED_CSV,
            PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_RES_BALANCED_CSV,
        )
    else:
        result_paths = (
            PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_PRED_NONE_CSV,
            PATH_SKINDESEASES_PREPROCESSING_STABLEDIFF_RES_NONE_CSV,
        )

    return (
        pd.read_csv(result_paths[0]),
        pd.read_csv(result_paths[1]),
    )


def preprocessing_algorithm_LearnedFairRepresentations(
    dataset: pd.DataFrame,
    dataset_id: str,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> pd.DataFrame:

    target_feat = targets[0]
    sensitive_feat = sensitive[0]

    X, y = (
        dataset[[col for col in dataset.columns if col != target_feat]],
        dataset[target_feat],
    )

    mitigator = LFR(
        unprivileged_groups=[{sensitive_feat: 0}],
        privileged_groups=[{sensitive_feat: 1}],
        **_filter_keys(kwargs, "k", "Ax", "Ay", "Az", "seed"),
        seed=0,
    )
    wrapper = AIF360PreprocWrapper(
        aif360_model=mitigator, sensitive_feature=sensitive_feat
    )

    wrapper.fit(X, y)
    X_t = wrapper.transform(X, y, decode=True)
    transformed_df = pd.concat(
        [
            X_t.reset_index(drop=True).drop("label", axis=1),
            y.reset_index(drop=True),
        ],
        axis=1,
    )

    prediction_df, result_df = inprocessing_algorithm_no_mitigation(
        dataset,
        transformed_df,
        sensitive,
        targets,
        **_filter_keys(kwargs, "hidden_dim", "hidden_layers", "epochs"),
    )

    return prediction_df, result_df


def preprocessing_algorithm_CorrelationRemover(
    dataset: pd.DataFrame,
    dataset_id: str,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> pd.DataFrame:

    target_feat = targets[0]
    sensitive_feat = sensitive[0]
    X, y = (
        dataset[[col for col in dataset.columns if col != target_feat]],
        dataset[target_feat],
    )

    feature_names = X.columns
    selected_sensitive_index = [
        idx for idx, elem in enumerate(feature_names) if sensitive_feat == elem
    ]
    corr_remover = CorrelationRemover(
        sensitive_feature_ids=selected_sensitive_index, **_filter_keys(kwargs, "alpha")
    )
    X_t = corr_remover.fit_transform(_discretize_columns(X).to_numpy(), y.to_numpy)
    transformed_df = pd.concat(
        [
            pd.DataFrame(
                X_t,
                columns=[elem for elem in feature_names if elem != sensitive_feat],
            ),
            X[sensitive_feat].reset_index(drop=True),
            y.reset_index(drop=True),
        ],
        axis=1,
    )

    prediction_df, result_df = inprocessing_algorithm_no_mitigation(
        dataset,
        transformed_df,
        sensitive,
        targets,
        **_filter_keys(kwargs, "hidden_dim", "hidden_layers", "epochs"),
    )

    return prediction_df, result_df


def inprocessing_algorithm_no_mitigation(
    original_dataset: pd.DataFrame,
    transformed_dataset: pd.DataFrame,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> pd.DataFrame:

    # -------------------------
    # 1) encode categories based on original_dataset (consistent mapping)
    # -------------------------
    label_maps = {}
    orig = original_dataset.copy()
    trans = transformed_dataset.copy()

    for col in orig.columns:
        if col in targets:
            # factorize target to integers and keep mapping
            codes, uniques = pd.factorize(orig[col])
            orig[col] = codes
            label_maps[col] = uniques
            # map transformed dataset target using same uniques (unseen -> -1 -> map to 0)
            if col in trans.columns:
                trans[col] = pd.Categorical(trans[col], categories=uniques).codes
                trans[col] = trans[col].replace(-1, 0)
        else:
            if orig[col].dtype == "object" or orig[col].dtype.name == "category":
                codes, uniques = pd.factorize(orig[col])
                orig[col] = codes
                label_maps[col] = uniques
                if col in trans.columns:
                    trans[col] = pd.Categorical(trans[col], categories=uniques).codes
                    trans[col] = trans[col].replace(-1, 0)
            else:
                # numeric column, leave as is; for transformed dataset try to coerce to numeric
                if col in trans.columns:
                    try:
                        trans[col] = pd.to_numeric(trans[col])
                    except Exception:
                        pass

    # ensure no NaNs remain (simple strategy: fill with 0)
    orig = orig.fillna(0)
    trans = trans.fillna(0)

    # -------------------------
    # 2) Setup KFold and bookkeeping
    # -------------------------
    n_splits = kwargs.get("n_splits", 2)
    metric_name_dict = {
        "performance": ["Accuracy", "Precision", "Recall", "Roc Auc", "F1"],
        "fairness": ["Demographic Parity Ratio", "Equalized Odds Ratio"],
    }
    n_metrics = len(metric_name_dict["performance"] + metric_name_dict["fairness"])
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    y = orig[targets[0]]
    X = orig.drop(columns=targets[0])

    fold_list = [
        x
        for fold_lst in [[fold_idx] * n_metrics for fold_idx in range(n_splits)]
        for x in fold_lst
    ]

    metric_type_list = [
        key
        for key in metric_name_dict.keys()
        for _ in range(len(metric_name_dict[key]))
    ] * n_splits
    metric_list = [
        metric_name for lst in metric_name_dict.values() for metric_name in lst
    ] * n_splits
    value_mitig_list = []
    value_nomitig_list = []
    value_pol_list = [0.0 for _ in range(n_metrics * n_splits)]

    predictions = np.zeros(len(original_dataset), dtype=float)

    # -------------------------
    # 3) K-Fold loop
    # -------------------------
    for fold, (train_idx, test_idx) in enumerate(kfold.split(X, y), 1):
        print(f"Fold: {fold}")

        for mitig_value in ["mitig", "nomitig"]:
            # choose dataset for this run
            if mitig_value == "nomitig":
                df_all = orig
            else:
                df_all = trans

            # slice train/test using positional indices (loc with index labels must match)
            train_df = df_all.iloc[train_idx].reset_index(drop=True)
            test_df = df_all.iloc[test_idx].reset_index(drop=True)

            # create tensors (drop target column for features)
            X_df_train = train_df.drop(columns=targets)
            y_df_train = train_df[targets[0]]
            X_df_test = test_df.drop(columns=targets)
            y_df_test = test_df[targets[0]]

            # Ensure labels are 1-D float arrays
            X_tensor_train = torch.tensor(
                X_df_train.values.astype(np.float32), dtype=torch.float32
            )
            y_tensor_train = torch.tensor(
                y_df_train.values.astype(np.float32), dtype=torch.float32
            ).reshape(-1)
            X_tensor_test = torch.tensor(
                X_df_test.values.astype(np.float32), dtype=torch.float32
            )
            y_tensor_test = torch.tensor(
                y_df_test.values.astype(np.float32), dtype=torch.float32
            ).reshape(-1)

            train_dataset = TensorDataset(X_tensor_train, y_tensor_train)
            train_loader = DataLoader(
                train_dataset, batch_size=kwargs.get("batch_size", 128), shuffle=True
            )

            test_dataset = TensorDataset(X_tensor_test, y_tensor_test)
            test_loader = DataLoader(
                test_dataset, batch_size=kwargs.get("batch_size", 128), shuffle=False
            )

            # -------------------------
            # model, loss, optimizer
            # -------------------------
            base_model = BaseModel(
                input_dim=orig.drop(columns=[targets[0]]).shape[1],
                hidden_dim=kwargs["hidden_dim"],
                hidden_layers=kwargs["hidden_layers"],
                output_dim=1,
            )
            learning_rate = kwargs.get("learning_rate", 1e-2)
            epochs = int(kwargs.get("epochs", 10))

            criterion = nn.BCELoss()
            optimizer = torch.optim.Adam(base_model.parameters(), lr=learning_rate)

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            base_model = base_model.to(device)

            # -------------------------
            # training loop (ensure shapes match)
            # -------------------------
            base_model.train()
            for epoch in range(epochs):
                epoch_loss = 0.0
                for batch_x, batch_y in train_loader:
                    batch_x = batch_x.to(device)
                    batch_y = batch_y.to(device).reshape(-1)

                    optimizer.zero_grad()

                    outputs = base_model(batch_x).squeeze(1)  # [batch]
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()

                    epoch_loss += loss.item()

            # -------------------------
            # prediction on test set (collect scalars)
            # -------------------------
            base_model.eval()
            all_y = []
            all_preds = []
            all_probs = []

            with torch.no_grad():
                for batch_x, batch_y in test_loader:
                    batch_x = batch_x.to(device)
                    batch_y = batch_y.to(device).reshape(-1)

                    probs = base_model(batch_x).squeeze(1)  # tensor [batch]
                    preds = (probs > 0.5).long()  # tensor [batch] (0/1)

                    all_probs.extend(probs.cpu().numpy().reshape(-1).tolist())
                    all_preds.extend(preds.cpu().numpy().reshape(-1).tolist())
                    all_y.extend(batch_y.cpu().numpy().reshape(-1).tolist())

            # -------------------------
            # compute metrics (use numpy arrays)
            # -------------------------
            y_true = np.array(all_y)
            y_pred_labels = np.array(all_preds)
            y_pred_probs = np.array(all_probs)

            # sklearn metrics (imported in your environment)
            accuracy = accuracy_score(y_true, y_pred_labels)
            precision = precision_score(y_true, y_pred_labels, zero_division=0)
            recall = recall_score(y_true, y_pred_labels, zero_division=0)
            roc_auc = (
                roc_auc_score(y_true, y_pred_probs)
                if len(np.unique(y_true)) > 1
                else 0.0
            )
            f1 = f1_score(y_true, y_pred_labels, zero_division=0)

            # fairness metrics (assume these accept arrays / DataFrame columns)
            # test_df currently corresponds to the test set used above
            dpr = demographic_parity_ratio(
                y_true, y_pred_labels, sensitive_features=test_df[sensitive]
            )
            eor = equalized_odds_ratio(
                y_true, y_pred_labels, sensitive_features=test_df[sensitive]
            )

            if mitig_value == "mitig":
                value_mitig_list.extend(
                    [accuracy, precision, recall, roc_auc, f1, dpr, eor]
                )
                # assign predictions into global array — ensure 1D scalar list
                predictions[test_idx] = y_pred_labels.tolist()
            else:
                value_nomitig_list.extend(
                    [accuracy, precision, recall, roc_auc, f1, dpr, eor]
                )

    # -------------------------
    # Build predictions dataframe (map target codes back to original labels if present)
    # -------------------------
    predictions_df = original_dataset.copy()
    for target in targets:
        # predictions are numeric codes; map back only if a mapping exists
        if target in label_maps:
            uniques = label_maps[target]
            preds_series = (
                pd.Series(predictions)
                .astype(int)
                .map(
                    lambda idx: uniques[idx] if 0 <= idx < len(uniques) else uniques[0]
                )
            )
            predictions_df[target] = preds_series.values
        else:
            predictions_df[target] = predictions

    results_df = pd.DataFrame(
        {
            "fold": fold_list,
            "metric_type": metric_type_list,
            "metric": metric_list,
            "value_mitig": value_mitig_list,
            "value_nomitig": value_nomitig_list,
            "value_pol": value_pol_list,
        }
    )

    return predictions_df, results_df


def generate_preprocessing_plot_picture(
    transformed_dataset: pd.DataFrame, file: io.BytesIO, **kwargs
):
    final_sample = (
        _discretize_columns(kwargs["original_dataset"])
        .drop(kwargs["class_feature"], axis=1)
        .reset_index(drop=True)
        .sample(
            n=min(PREPROCESSING_SAMPLE_SIZE, len(kwargs["original_dataset"])),
            random_state=42,
        )
        .copy()
    )
    trans_sample = (
        _discretize_columns(transformed_dataset)
        .drop(kwargs["class_feature"], axis=1)
        .reset_index(drop=True)
        .sample(
            n=min(PREPROCESSING_SAMPLE_SIZE, len(transformed_dataset)), random_state=42
        )
        .copy()
    )

    # 3) Tag each subset with a "source"
    final_sample["source"] = "Original"
    trans_sample["source"] = "Transformed"

    # 4) Concatenate them
    combined = pd.concat([final_sample, trans_sample], ignore_index=True)

    # 5) Parallel Coordinates expects one categorical column (here "source") to color the lines
    plt.figure(figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE))
    parallel_coordinates(
        combined,
        class_column="source",
        color=["blue", "red"],  # or other color palette
        alpha=0.5,
    )
    plt.title("Parallel Coordinates: final_df vs. transformed_df")
    plt.ylabel("Feature Value")

    # Make feature names vertical to avoid overlap
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.gcf().savefig(file, format="svg", dpi=FIG_DPI)


class PreProcessingRequestedReaction(AbstractProcessingRequestedReaction):
    def __init__(self):
        super().__init__("pre")

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        metrics: list[str],
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        algorithm, result = self._call_global_algorithm(
            dataset,
            dataset_id,
            targets,
            sensitive,
            proxies,
            detected,
            hyperparameters,
            prefix=phase,
        )
        computed_metrics = None
        if isinstance(result, tuple):
            assert len(result) == 2, "Expected a tuple of two dataframes"
            result, computed_metrics = result
        assert isinstance(
            result, pd.DataFrame
        ), f"Expected dataframe, got {type(result)}: {result!r}"
        result_id = self.next_name(dataset_id)
        self.log("New dataset id: %s", result_id)
        cases = []

        try:
            # if computed_metrics is None:
            #     computed_metrics: pd.DataFrame = inprocessing_algorithm_no_mitigation(
            #         dataset, dataset_id, targets, sensitive
            #     )
            cases += [
                (
                    f"preprocessing_plot__{result_id}",
                    lambda: generate_plot(
                        "preprocessing",
                        result,
                        **{
                            "original_dataset": dataset,
                            "class_feature": targets[0],
                        },
                    ),
                ),
            ]
            cases += [
                (
                    # used by on_polarization_requested.py
                    f"computed_metrics__{algorithm}__{dataset_id}",
                    lambda: to_csv(computed_metrics),
                ),
                (
                    f"performance_plot__{result_id}",
                    lambda: generate_plot("performance", computed_metrics),
                ),
                (
                    f"fairness_plot__{result_id}",
                    lambda: generate_plot("fairness", computed_metrics),
                ),
            ]
        except Exception as e:
            self.log_error("Failed to compute no_mitigations metrics", error=e)

        lambda_metrics = lambda: generate_metrics(result, sensitive, targets, metrics)
        lambda_selected_metrics = lambda: selected_metrics(
            json.loads(lambda_metrics()), detected
        )
        cases = [
            (f"dataset__{result_id}", lambda: to_csv(result)),
            (f"dataset_head__{result_id}", lambda: to_csv(get_heads(result))),
            (f"stats__{result_id}", lambda: to_csv(get_stats(result))),
            (
                f"correlation_matrix__{result_id}",
                lambda: correlation_matrix_picture(result),
            ),
            (f"metrics__{result_id}", lambda_metrics),
            (f"selected_metrics__{result_id}", lambda_selected_metrics),
        ] + cases
        for k, v in cases:
            try:
                yield k, v()
            except Exception as e:
                self.log_error("Failed to produce %s", k, error=e)


# def _encode_single_feature(
#     df: pd.DataFrame, feature: str, favorable_label: str
# ) -> pd.DataFrame:

#     df_encoded = df.copy()

#     if feature in df_encoded.columns:
#         df_encoded[feature] = df_encoded[feature].apply(
#             lambda x: 1 if x == favorable_label else 0
#         )
#     return df_encoded


# def _compute_fair_metric(
#     fair_metric_name: str,
#     settings: dict,
#     X: pd.DataFrame,
#     y_true: pd.Series,
#     y_pred: pd.Series,
# ) -> float:
#     fair_metric_scorer = getattr(fairlearn_metrics, fair_metric_name)

#     X_sensitive = _encode_single_feature(
#         df=X,
#         feature=settings["sensitive_feat"],
#         favorable_label=settings["favorable_sensitive_label"],
#     )
#     X_sensitive = X_sensitive[settings["sensitive_feat"]]

#     return fair_metric_scorer(
#         y_true=y_true,
#         y_pred=y_pred,
#         sensitive_features=X_sensitive,
#     )


def _generate_random_number(min_value: float, max_value: float) -> float:
    return random.uniform(min_value, max_value)


class BaseModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, hidden_layers: int, output_dim):
        super(BaseModel, self).__init__()
        layers = []
        layers.append(nn.Linear(input_dim, hidden_dim))
        layers.append(nn.ReLU())

        for _ in range(hidden_layers - 1):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.ReLU())

        layers.append(nn.Linear(hidden_dim, output_dim))
        layers.append(nn.Sigmoid())

        # Combine into a single sequential model
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)


def inprocessing_algorithm_general(
    algorithm: str,
    dataset: pd.DataFrame,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> tuple:

    reg_hyperparam, reg_hyperparam_value = None, None
    hyperparams = []
    model_cls: Processor
    if algorithm == "FaUCI":
        model_cls = Fauci
        reg_hyperparam = "regularization_weight"
    elif algorithm == "AdversarialDebiasing":
        model_cls = AdversarialDebiasing
        reg_hyperparam = "lambda_adv"
        hyperparams = ["input_dim", "hidden_dim", "output_dim", "sensitive_dim"]
    elif algorithm == "PrejudiceRemover":
        model_cls = PrejudiceRemover
        reg_hyperparam = "eta"
    else:
        reg_hyperparam = None

    if reg_hyperparam is not None:
        reg_hyperparam_value = kwargs[reg_hyperparam]
    else:
        raise Exception("Invalid algorithm")
    hyperparams += [reg_hyperparam]

    df = FairDataFrame(dataset.copy())

    df.targets = targets
    df.sensitive = sensitive

    label_maps = {}

    for col in df.columns:
        if df[col].dtype == "object" or df[col].dtype == "category":
            df[col], uniques = pd.factorize(df[col])
            label_maps[col] = uniques

    print(f"Dataset Form: {df.shape}")
    print(f"Target Column: {df.targets}")
    print(f"Sensitive Attributes: {df.sensitive}")

    ########################### K-FOLD ##################################################
    n_splits = 5
    metric_name_dict = {
        "performance": ["Accuracy", "Precision", "Recall", "Roc Auc", "F1"],
        "fairness": ["Demographic Parity Ratio", "Equalized Odds Ratio"],
    }
    n_metrics = len(metric_name_dict["performance"] + metric_name_dict["fairness"])
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    y = df[targets[0]]
    X = df.drop(columns=targets[0])

    fold_list = [
        x
        for fold_lst in [[fold_idx] * n_metrics for fold_idx in range(n_splits)]
        for x in fold_lst
    ]

    metric_type_list = [
        key
        for key in metric_name_dict.keys()
        for _ in range(len(metric_name_dict[key]))
    ] * n_splits
    metric_list = [
        metric_name for lst in metric_name_dict.values() for metric_name in lst
    ] * n_splits
    value_mitig_list = []
    value_nomitig_list = []
    value_pol_list = [0.0 for _ in range(n_metrics * n_splits)]

    predictions = np.zeros(
        len(dataset)
    )  # store predictions to return predictions dataframe later

    for fold, (train_idx, test_idx) in enumerate(kfold.split(X, y), 1):

        logger.info(f"Fold: {fold}")

        train_df = df.loc[train_idx]
        test_df = df.loc[test_idx]

        train_df = FairDataFrame(train_df)
        train_df.targets = targets
        train_df.sensitive = sensitive

        ############### LOOPING OVER MITIG (REG_WEIGHTS=0.0) AND NOMITIG (REG_WEIGHTS=VALUE) ###########
        # First we use the user-defined regularization_weight, then we put
        # kwargs[regularization_weight] = 0.0 to compute the nomitig values.

        for mitig_value in ["mitig", "nomitig"]:
            logger.info(f"\tMitigation: {mitig_value == 'mitig'}")
            # putting kwargs[regularization_weight] = 0.0 to compute the nomitig values
            if mitig_value == "nomitig":
                kwargs[reg_hyperparam] = 0.0
            elif mitig_value == "mitig":
                kwargs[reg_hyperparam] = reg_hyperparam_value

            ################################## TRAINING AND EVALUATING FAUCI MODEL #########################
            hyperparams_value = {
                key: kwargs[key] for key in kwargs.keys() if key in hyperparams
            }

            base_model = BaseModel(
                input_dim=kwargs["input_dim"],
                hidden_dim=kwargs["hidden_dim"],
                hidden_layers=kwargs["hidden_layers"],
                output_dim=kwargs["output_dim"],
            )
            epochs: int = kwargs["epochs"]
            batch_size: int = 128
            if algorithm in ["FaUCI", "PrejudiceRemover"]:
                mitigated_model = model_cls(torchModel=base_model, **hyperparams_value)
                mitigated_model.fit(
                    train_df, epochs=epochs, batch_size=batch_size, verbose=False
                )
                base_model.eval()
            else:
                mitigated_model = model_cls(**hyperparams_value)
                mitigated_model.fit(
                    train_df.drop(columns=[targets[0]]),
                    train_df[targets[0]],
                    epochs=epochs,
                    batch_size=batch_size,
                    verbose=False,
                )

            with torch.no_grad():
                X_test = FairDataFrame(test_df.drop(columns=targets[0]))
                y_test = test_df[targets[0]]
                y_pred_base = mitigated_model.predict(X_test)
                y_pred_base_binary = (y_pred_base > 0.5).float()

                y_pred_baseline = y_pred_base_binary.detach().cpu().numpy()

                accuracy = accuracy_score(y_test, y_pred_baseline)
                precision = precision_score(y_test, y_pred_baseline)
                recall = recall_score(y_test, y_pred_baseline)
                roc_auc = roc_auc_score(y_test, y_pred_base)
                f1 = f1_score(y_test, y_pred_baseline)

                dpr = demographic_parity_ratio(
                    y_test, y_pred_baseline, sensitive_features=X_test[sensitive]
                )
                eor = equalized_odds_ratio(
                    y_test, y_pred_baseline, sensitive_features=X_test[sensitive]
                )

                if mitig_value == "mitig":
                    value_mitig_list.extend(
                        [accuracy, precision, recall, roc_auc, f1, dpr, eor]
                    )
                    predictions[test_idx] = list(
                        y_pred_baseline.flatten()
                    )  # store the predictions in the correct positions
                elif mitig_value == "nomitig":
                    value_nomitig_list.extend(
                        [accuracy, precision, recall, roc_auc, f1, dpr, eor]
                    )

    # build the dataset we want to return, with the predictions
    # instead of the targets
    predictions_df = dataset.copy()

    for target in targets:
        predictions_df[target] = predictions
        predictions_df[target] = label_maps[target].take(predictions_df[target])

    results_df = pd.DataFrame(
        {
            "fold": fold_list,
            "metric_type": metric_type_list,
            "metric": metric_list,
            "value_mitig": value_mitig_list,
            "value_nomitig": value_nomitig_list,
            "value_pol": value_pol_list,
        }
    )

    return (
        predictions_df,
        results_df,
    )


def inprocessing_algorithm_FaUCI(
    dataset: pd.DataFrame,
    dataset_id: str,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> tuple:

    if "Akkodis" in dataset_id:
        new_dataset = read_csv(dataset_path("akkodis"))
        if kwargs["lambda"] >= 0.5:
            result_path = PATH_AKKODIS_FAUCI_RES_1_CSV
        else:
            result_path = PATH_AKKODIS_BASELINE_RES_1_CSV
        return (
            new_dataset,
            pd.read_csv(result_path),
        )

    if "Adult" in dataset_id:
        new_dataset = (
            read_csv(dataset_path("fauci_predictions"))
            .drop("class", axis=1)
            .rename(columns={"predictions": "class"})
        )
        if kwargs["lambda"] == 0:
            result_path = PATH_INPROCESSING_FAUCI_RES_0_CSV
        elif kwargs["lambda"] == 1:
            result_path = PATH_INPROCESSING_FAUCI_RES_1_CSV
        else:
            result_path = PATH_INPROCESSING_FAUCI_RES_CSV
        return (
            new_dataset,
            pd.read_csv(result_path),
        )

    predictions_df, results_df = inprocessing_algorithm_general(
        algorithm="FaUCI",
        dataset=dataset,
        sensitive=[sensitive[0]],
        targets=[targets[0]],
        input_dim=dataset.drop(columns=[targets[0]]).shape[1],
        hidden_dim=kwargs["hidden_dim"],
        hidden_layers=kwargs["hidden_layers"],
        output_dim=1,
        sensitive_dim=1,
        epochs=kwargs["epochs"],
        regularization_weight=kwargs["lambda"],
    )

    return (
        predictions_df,
        results_df,
    )


def inprocessing_algorithm_PrejudiceRemover(
    dataset: pd.DataFrame,
    dataset_id: str,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> tuple:

    predictions_df, results_df = inprocessing_algorithm_general(
        algorithm="PrejudiceRemover",
        dataset=dataset,
        sensitive=[sensitive[0]],
        targets=[targets[0]],
        input_dim=dataset.drop(columns=[targets[0]]).shape[1],
        hidden_dim=kwargs["hidden_dim"],
        hidden_layers=kwargs["hidden_layers"],
        output_dim=1,
        sensitive_dim=1,
        epochs=kwargs["epochs"],
        eta=kwargs["eta"],
    )

    return predictions_df, results_df


def inprocessing_algorithm_AdversarialDebiasing(
    dataset: pd.DataFrame,
    dataset_id: str,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> tuple:

    # TODO: to remove
    if "cand_provenance_gender" in sensitive or "Sensitive" in sensitive:
        if "cand_provenance_gender" in sensitive:
            if kwargs["lambda_adv"] == 0:
                result_paths = (
                    PATH_ADECCO_INPROCESSING_ADVDEB_PRED_0_CSV,
                    PATH_ADECCO_INPROCESSING_ADVDEB_RES_0_CSV,
                )
            elif kwargs["lambda_adv"] == 1:
                result_paths = (
                    PATH_ADECCO_INPROCESSING_ADVDEB_PRED_1_CSV,
                    PATH_ADECCO_INPROCESSING_ADVDEB_RES_1_CSV,
                )
            else:
                result_paths = (
                    PATH_ADECCO_INPROCESSING_ADVDEB_PRED_2_CSV,
                    PATH_ADECCO_INPROCESSING_ADVDEB_RES_2_CSV,
                )
        else:
            if kwargs["lambda_adv"] == 0:
                result_paths = (
                    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_0_CSV,
                    PATH_AKKODIS_INPROCESSING_ADVDEB_RES_0_CSV,
                )
            elif kwargs["lambda_adv"] == 1:
                result_paths = (
                    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_1_CSV,
                    PATH_AKKODIS_INPROCESSING_ADVDEB_RES_1_CSV,
                )
            else:
                result_paths = (
                    PATH_AKKODIS_INPROCESSING_ADVDEB_PRED_CSV,
                    PATH_AKKODIS_INPROCESSING_ADVDEB_RES_CSV,
                )

        return (
            pd.read_csv(result_paths[0]),
            pd.read_csv(result_paths[1]),
        )

    predictions_df, results_df = inprocessing_algorithm_general(
        algorithm="AdversarialDebiasing",
        dataset=dataset,
        sensitive=[sensitive[0]],
        targets=[targets[0]],
        input_dim=dataset.drop(columns=[targets[0]]).shape[1],
        hidden_dim=kwargs["hidden_dim"],
        hidden_layers=kwargs["hidden_layers"],
        output_dim=1,
        sensitive_dim=1,
        epochs=kwargs["epochs"],
        lambda_adv=kwargs["lambda_adv"],
    )

    return predictions_df, results_df


def inprocessing_algorithm_ContributionBasedClassifier(
    dataset: pd.DataFrame,
    dataset_id: str,
    sensitive: list[str],
    targets: list[str],
    **kwargs,
) -> tuple:

    if kwargs["fairness_mechanism"] == "unawareness":
        result_paths = (
            PATH_ULL_INPROCESSING_BASELINE_PRED_CSV,
            PATH_ULL_INPROCESSING_BASELINE_RES_POL_1_CSV,
        )
    else:
        result_paths = (
            PATH_ULL_INPROCESSING_BEST_PRED_CSV,
            PATH_ULL_INPROCESSING_BEST_RES_POL_1_CSV,
        )

    return (
        pd.read_csv(result_paths[0]),
        pd.read_csv(result_paths[1]),
    )


def generate_standard_plot_pictures(
    plot_type: str, results: pd.DataFrame, file: io.BytesIO
):
    fig, axes = plt.subplots(
        1, 2, figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE), sharey=True
    )

    color = "Blues" if plot_type == "performance" else "Purples"

    sns.barplot(
        data=results,
        x="metric",
        y="value_nomitig",
        hue="metric",
        errorbar="sd",  # Seaborn 0.12+
        capsize=0.1,
        palette=f"{color}_r",
        ax=axes[0],
    )
    axes[0].set_title(
        f"{plot_type.title()} with No Mitigation\n(mean ± std across folds)"
    )
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Value")
    axes[0].legend([], [], frameon=False)  # hide legend if redundant
    axes[0].set_ylim([0, 1])

    sns.barplot(
        data=results,
        x="metric",
        y="value_mitig",
        hue="metric",
        errorbar="sd",
        capsize=0.1,
        palette=f"{color}_r",
        ax=axes[1],
    )
    axes[1].set_title(f"{plot_type.title()} with Mitigation\n(mean ± std across folds)")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Value")

    plt.tight_layout()
    fig.savefig(file, format="svg", dpi=FIG_DPI)


def generate_polarization_plot_pictures(results: pd.DataFrame, file: io.BytesIO):
    fig, axes = plt.subplots(
        1, 2, figsize=(FIG_WIDTH_SIZE, FIG_HEIGHT_SIZE), sharey=True
    )

    sns.barplot(
        data=results[results["metric_type"] == "performance"],
        x="metric",
        y="value_pol",
        hue="metric",
        errorbar="sd",  # Seaborn 0.12+
        capsize=0.1,
        palette="Blues_r",
        ax=axes[0],
    )
    axes[0].set_title(f"Performance with Polarized Dataset\n(mean ± std across folds)")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Value")
    axes[0].legend([], [], frameon=False)  # hide legend if redundant
    axes[0].set_ylim([0, 1])

    sns.barplot(
        data=results[results["metric_type"] == "fairness"],
        x="metric",
        y="value_pol",
        hue="metric",
        errorbar="sd",
        capsize=0.1,
        palette="Purples_r",
        ax=axes[1],
    )
    axes[1].set_title(f"Fairness with Polarized Dataset\n(mean ± std across folds)")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Value")

    plt.tight_layout()
    fig.savefig(file, format="svg", dpi=FIG_DPI)


def generate_plot_picture(
    plot_type: str, results: pd.DataFrame, file: io.BytesIO, **kwargs
) -> io.BytesIO:
    if plot_type in ["performance", "fairness"]:
        filtered_results = results[results["metric_type"] == plot_type].copy()
        generate_standard_plot_pictures(plot_type, filtered_results, file)
    elif plot_type == "polarization":
        generate_polarization_plot_pictures(results, file)
    elif plot_type == "preprocessing":
        generate_preprocessing_plot_picture(results, file, **kwargs)
    else:
        raise Exception(f"No plot_type {plot_type}")

    svg_data = file.getvalue().decode("utf-8")
    modified_svg = svg_data.replace("<svg", f'<svg plot-type="{plot_type}_plot"', 1)
    updated_file = io.BytesIO(modified_svg.encode("utf-8"))
    return updated_file


def generate_plot(plot_type: str, results: pd.DataFrame, **kwargs) -> bytes:
    buffer = io.BytesIO()
    plot_picture_buffer: io.BytesIO = generate_plot_picture(
        plot_type=plot_type, results=results, file=buffer, **kwargs
    )
    return plot_picture_buffer.getvalue()


class InProcessingRequestedReaction(AbstractProcessingRequestedReaction):
    def __init__(self):
        super().__init__("in")

    def produce_info(
        self,
        phase: str,
        dataset_id: str,
        dataset: pd.DataFrame,
        metrics: list[str],
        targets: list[str],
        sensitive: list[str],
        proxies: dict,
        detected: dict,
        hyperparameters: dict,
    ) -> Iterable[tuple[str, Union[str, bytes]]]:
        algorithm, results = self._call_global_algorithm(
            dataset,
            dataset_id,
            targets,
            sensitive,
            proxies,
            detected,
            hyperparameters,
            prefix=phase,
        )
        assert isinstance(results, tuple)
        predictions: pd.DataFrame = results[0]
        predictions_head = predictions.head(100)
        computed_metrics: pd.DataFrame = results[1]

        if "Akkodis" in dataset_id and algorithm == "FaUCI":
            lambda_metrics = lambda: (
                PATH_AKKODIS_METRICS_FAUCI_ORIGINAL_JSON.read_text()
                if hyperparameters["lambda"] >= 0.5
                else PATH_AKKODIS_METRICS_BASELINE_ORIGINAL_JSON.read_text()
            )
        elif "Ull" in dataset_id and "fairness_mechanism" in hyperparameters:
            lambda_metrics = lambda: (
                PATH_ULL_METRICS_BASELINE_JSON.read_text()
                if hyperparameters["fairness_mechanism"] == "unawareness"
                else PATH_ULL_METRICS_BEST_JSON.read_text()
            )
        else:
            lambda_metrics = lambda: generate_metrics(
                predictions, sensitive, targets, metrics
            )
        selected_metrics_lambda = lambda: selected_metrics(
            json.loads(lambda_metrics()), detected
        )
        cases = [
            (
                f"predictions_head__{algorithm}__{dataset_id}",
                lambda: to_csv(predictions_head),
            ),
            (f"predictions__{algorithm}__{dataset_id}", lambda: to_csv(predictions)),
            (
                f"correlation_matrix__{algorithm}__{dataset_id}",
                lambda: correlation_matrix_picture(predictions),
            ),
            (
                f"metrics__{algorithm}__{dataset_id}",
                lambda_metrics,
            ),
            (f"selected_metrics__{algorithm}__{dataset_id}", selected_metrics_lambda),
            (
                f"performance_plot__{algorithm}__{dataset_id}",
                lambda: generate_plot("performance", computed_metrics),
            ),
            (
                f"fairness_plot__{algorithm}__{dataset_id}",
                lambda: generate_plot("fairness", computed_metrics),
            ),
            (
                # used by on_polarization_requested.py
                f"computed_metrics__{algorithm}__{dataset_id}",
                lambda: to_csv(computed_metrics),
            ),
        ]
        for k, v in cases:
            try:
                yield k, v()
            except Exception as e:
                self.log_error("Failed to produce %s", k, error=e)

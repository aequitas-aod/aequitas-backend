from pathlib import Path
import json


DIR = Path(__file__).parent


PATH_STATS_CSV = DIR / "stats.csv"
PATH_FEATURES_JSON = DIR / "features.json"
PATH_SUGGESTED_PROXIES_JSON = DIR / "suggested-proxies.json"
PATH_CORRELATION_MATRIX_SVG = DIR / "correlation-matrix.svg"
PATH_ACTUAL_DATASET_CSV = DIR / "actual-dataset.csv"
PATH_METRICS_JSON = DIR / "metrics.json"
PATH_DETECTED_JSON = DIR / "detected.json"
PATH_PROXIES_JSON = DIR / "proxies.json"
PATH_PREPROCESSING_JSON = DIR / "preprocessing.json"
PATH_PREPROCESSING_LFR_CSV = DIR / "preprocessed_lfr_result.csv"
PATH_PREPROCESSING_CR_CSV = DIR / "preprocessed_cr.csv"
PATH_INPROCESSING_JSON = DIR / "inprocessing.json"
PATH_INPROCESSING_FAUCI_PRED_CSV = DIR / "fauci_predictions_test.csv"
PATH_INPROCESSING_FAUCI_RES_CSV = DIR / "fauci_results.csv"
PATH_INPROCESSING_PERFORMANCE_SVG = DIR / "inprocessing-performance-plot.svg"
PATH_INPROCESSING_FAIRNESS_SVG = DIR / "inprocessing-fairness-plot.svg"
PATH_INPROCESSING_POLARIZATION_SVG = DIR / "inprocessing-polarization-plot.svg"


def get_json(name: str | Path) -> dict:
    if isinstance(name, str):
        path = DIR / f"{name}.json"
    else:
        path = name
    with path.open() as f:
        return json.load(f)

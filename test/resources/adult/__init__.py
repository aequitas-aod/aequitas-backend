from pathlib import Path
import json


DIR = Path(__file__).parent


PATH_STATS_CSV = DIR / "stats.csv"
PATH_FEATURES_JSON = DIR / "features.json"
PATH_SUGGESTED_PROXIES_JSON = DIR / "suggested-proxies.json"
PATH_CORRELATION_MATRIX_SVG = DIR / "correlation-matrix.svg"
PATH_ACTUAL_DATASET_CSV = DIR / "actual-dataset.csv"
PATH_ACTUAL_DATASET_ADULT_CSV = DIR / "adult.csv"
PATH_METRICS_JSON = DIR / "metrics.json"
PATH_DETECTED_JSON = DIR / "detected.json"
PATH_PROXIES_JSON = DIR / "proxies.json"
PATH_PREPROCESSING_JSON = DIR / "preprocessing.json"
PATH_PREPROCESSING_LFR_CSV = DIR / "preprocessed_lfr.csv"
PATH_PREPROCESSING_CR_CSV = DIR / "preprocessed_cr.csv"


def get_json(name: str | Path) -> dict:
    if isinstance(name, str):
        path = DIR / f"{name}.json"
    else:
        path = name
    with path.open() as f:
        return json.load(f)

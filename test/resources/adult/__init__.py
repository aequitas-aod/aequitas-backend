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


def get_json(name: str) -> dict:
    with open(DIR / f"{name}.json") as f:
        return json.load(f)

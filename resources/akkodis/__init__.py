from pathlib import Path
import json


DIR = Path(__file__).parent

PATH_INPROCESSING_ADVDEB_RES_0_CSV = DIR / "advdeb_akkodis_results_repair_0.csv"
PATH_INPROCESSING_ADVDEB_RES_CSV = DIR / "advdeb_akkodis_results_repair.csv"
PATH_INPROCESSING_ADVDEB_RES_1_CSV = DIR / "advdeb_akkodis_results_repair_1.csv"

PATH_INPROCESSING_ADVDEB_PRED_0_CSV = DIR / "akkodis_predict_0.csv"
PATH_INPROCESSING_ADVDEB_PRED_CSV = DIR / "akkodis_predict.csv"
PATH_INPROCESSING_ADVDEB_PRED_1_CSV = DIR / "akkodis_predict_1.csv"


def get_json(name: str | Path) -> dict:
    if isinstance(name, str):
        path = DIR / f"{name}.json"
    else:
        path = name
    with path.open() as f:
        return json.load(f)

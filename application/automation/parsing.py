import io
from typing import Optional

import numpy as np
import pandas as pd
import json


def to_csv(df: pd.DataFrame, path=None) -> Optional[str]:
    def _convert_to_json(x):
        if isinstance(x, (dict, list)):
            return json.dumps(x)
        return x

    df = _pythonize(df.copy())

    for col in df.columns:
        df[col] = df[col].apply(_convert_to_json)

    params = {"index": False, "quotechar": '"', "lineterminator": "\n"}
    if path:
        df.to_csv(path, **params)
    else:
        return df.to_csv(**params)


def to_json(obj, path=None) -> Optional[str]:
    obj = _pythonize(obj)
    if path is not None:
        with open(path, "w") as file:
            json.dump(obj, file, indent=4)
    else:
        return json.dumps(obj, indent=4)


def parse_json(text: str) -> dict:
    return json.loads(text)


def read_json(path) -> object:
    with open(path, "r") as file:
        return json.load(file)


def _upack_json_strings(df: pd.DataFrame) -> pd.DataFrame:
    def _parse_as_json(x):
        if not isinstance(x, str):
            return x
        try:
            return parse_json(x)
        except json.JSONDecodeError:
            return x

    for col in df.columns:
        df[col] = df[col].apply(_parse_as_json)
    return df


def _pythonize(obj):
    if isinstance(obj, pd.DataFrame):
        for col in obj.columns:
            obj[col] = obj[col].apply(_pythonize)
        return obj
    if isinstance(obj, list) or isinstance(obj, np.ndarray):
        return [_pythonize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _pythonize(v) for k, v in obj.items()}
    if hasattr(obj, "item"):
        obj = obj.item()
    if isinstance(obj, float):
        if np.isnan(obj):
            return ""
        if np.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
    return obj


def read_csv(path) -> pd.DataFrame:
    df = pd.read_csv(path, quotechar='"')
    return _upack_json_strings(df)


def parse_csv(text: str) -> pd.DataFrame:
    return read_csv(io.StringIO(text))

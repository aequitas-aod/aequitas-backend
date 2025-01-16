import io
from typing import Union

import pandas as pd
import json


def to_csv(df: pd.DataFrame, path=None) -> Union[str, None]:
    def _convert_to_json(x):
        if isinstance(x, (dict, list)):
            return json.dumps(x)
        return x

    df = df.copy()

    for col in df.columns:
        df[col] = df[col].apply(_convert_to_json)

    params = {"index": False, "quotechar": "'", "lineterminator": "\n"}
    if path:
        df.to_csv(path, **params)
    else:
        return df.to_csv(**params)


def to_json(obj) -> str:
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


def read_csv(path) -> pd.DataFrame:
    df = pd.read_csv(path, quotechar="'")
    return _upack_json_strings(df)


def parse_csv(text: str) -> pd.DataFrame:
    return read_csv(io.StringIO(text))

import io
import json

import pandas as pd


def parse_csv(text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(text))


def parse_json(text: str) -> dict:
    return json.loads(text)

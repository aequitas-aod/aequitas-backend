import io
import pandas as pd
import json

from domain.project.core import Project


def parse_csv(text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(text))


def parse_json(text: str) -> dict:
    return json.loads(text)


def get_context_key(project: Project, key: str, parse_as: str) -> object:
    parsing_function = globals().get(f"parse_{parse_as}")
    if parsing_function is None:
        raise ValueError(f"Unknown parsing function: {__name__}.parse_{parse_as}")
    return parsing_function(project.get_from_context(key))

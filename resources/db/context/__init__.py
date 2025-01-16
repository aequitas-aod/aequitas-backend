from pathlib import Path
import yaml
import json


DIR = Path(__file__).parent


def context_path(name: str) -> Path:
    return DIR / f"{name}.yml"


def context_data(name: str) -> dict:
    return yaml.safe_load(context_path(name).read_text())


def context_data_json(name: str) -> str:
    data = context_data(name)
    return json.dumps(data, indent=4)

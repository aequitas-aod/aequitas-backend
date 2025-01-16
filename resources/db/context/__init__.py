from pathlib import Path
import yaml


DIR = Path(__file__).parent


def context_path(name: str) -> Path:
    return DIR / f"{name}.yml"


def context_data(name: str) -> dict:
    return yaml.safe_load(context_path(name).read_text())

from pathlib import Path


DIR = Path(__file__).parent


def stats_path(name: str) -> Path:
    return DIR / f"{name}.csv"
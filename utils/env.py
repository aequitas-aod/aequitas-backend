import os
from pathlib import Path

from dotenv import load_dotenv

_home = Path.home()

_descending_priority_env_paths = [
    Path(os.getcwd()) / ".env",
    _home / ".aequitas" / ".env",
]


def _get_env_var_or_fail(var_name: str) -> str:
    value = os.environ.get(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} not set")
    return value


for path in _descending_priority_env_paths:
    if path.exists():
        load_dotenv(path, override=False)

ENV = _get_env_var_or_fail("ENV")

FLASK_ENV = os.getenv("FLASK_ENV")
DB_HOST = "localhost" if FLASK_ENV == "develop" else _get_env_var_or_fail("DB_HOST")
DB_USER = _get_env_var_or_fail("DB_USER")

if DB_USER != "neo4j":
    raise ValueError("Only neo4j is supported as database user")

DB_PASSWORD = _get_env_var_or_fail("DB_PASSWORD")

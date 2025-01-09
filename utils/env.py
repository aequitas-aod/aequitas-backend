import os
from pathlib import Path
from warnings import warn
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


def is_testing() -> bool:
    return any(s in ENV for s in ["dev", "test"])


DB_HOST = _get_env_var_or_fail("DB_HOST")
DB_USER = _get_env_var_or_fail("DB_USER")

if DB_USER != "neo4j":
    raise ValueError("Only neo4j is supported as database user")

DB_PASSWORD = _get_env_var_or_fail("DB_PASSWORD")


if is_testing() and DB_HOST != "localhost":
    warn(
        "Testing environment is not using `localhost` as the database hostname. "
        "Consider setting the `DB_HOST` environment variable to `localhost`.",
        RuntimeWarning,
        stacklevel=2,
    )


def force_local_db():
    DB_HOST = "localhost"


def environ():
    return os.environ.copy()

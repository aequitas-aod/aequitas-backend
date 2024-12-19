import pathlib
from functools import cache
from utils.logs import logger
import re


DIR_TEST = pathlib.Path(__file__).parent
DIR_RESOURCES = DIR_TEST / "resources"

PATH_EXAMPLE_QUESTION_GRAPH = DIR_RESOURCES / "question-graph-example.yml"
PATH_EXAMPLE_QUESTIONS_LOAD = DIR_RESOURCES / "questions-load-example.yml"
PATH_DOCKER_COMPOSE_TEMPLATE = DIR_RESOURCES / "docker-compose.yml.template"


@cache
def get_resource_text(path: pathlib.Path | str) -> str:
    with open(path, "r") as file:
        return file.read()


def example_question_graph() -> str:
    return get_resource_text(PATH_EXAMPLE_QUESTION_GRAPH)


def example_questions_load() -> str:
    return get_resource_text(PATH_EXAMPLE_QUESTIONS_LOAD)


def docker_compose_template() -> str:
    return get_resource_text(PATH_DOCKER_COMPOSE_TEMPLATE)


PATTERN_METAVARIABLE = re.compile(r"__([A-Z_][A-Za-z0-9_]+)__")


def _spot_metavariables(text: str) -> set[str]:
    return {m.group(1) for m in PATTERN_METAVARIABLE.finditer(text)}


def docker_compose_spec(**kwargs) -> str:
    from utils.env import environ

    env = environ()
    env.update(kwargs)
    template = docker_compose_template()
    spec = ""
    for line in template.splitlines():
        for metavariable, value in env.items():
            line = line.replace(f"__{metavariable}__", value)
        spec += line + "\n"
    for metavariable in _spot_metavariables(spec):
        logger.warning(
            f"Unassigned meta-variable {metavariable} in Docker Compose spec"
        )
    return spec

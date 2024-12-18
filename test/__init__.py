import pathlib
from functools import cache


DIR_TEST = pathlib.Path(__file__).parent
DIR_RESOURCES = DIR_TEST / "resources"

PATH_EXAMPLE_QUESTION_GRAPH = DIR_RESOURCES / "question-graph-example.yml"
PATH_EXAMPLE_QUESTIONS_LOAD = DIR_RESOURCES / "questions-load-example.yml"


@cache
def get_resource_text(path: pathlib.Path | str) -> str:
    with open(path, "r") as file:
        return file.read()


def example_question_graph() -> str:
    return get_resource_text(PATH_EXAMPLE_QUESTION_GRAPH)


def example_questions_load() -> str:
    return get_resource_text(PATH_EXAMPLE_QUESTIONS_LOAD)

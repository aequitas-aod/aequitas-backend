import pathlib
from importlib import import_module

import pandas as pd
from kafka.consumer.fetcher import ConsumerRecord
from presentation.presentation import deserialize
from application.events import EventsService
from typing import Iterable
from domain.common.core import EntityId
from domain.project.core import Project
from utils.logs import logger


class DynamicObject:
    def __init__(self, data: dict = None, **kwargs):
        self.update(data, **kwargs)

    def update(self, data: dict = None, **kwargs):
        for key, value in (data or {}).items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)


class Automator:
    def __init__(self, topics: Iterable[str], components: dict = None):
        assert topics, "Some topic must be provided"
        self.__topics: set[str] = set(topics or [])
        self.__components: DynamicObject = DynamicObject(components or {})

    @property
    def topics(self) -> set[str]:
        return set(self.__topics)

    @property
    def components(self) -> DynamicObject:
        return self.__components

    @components.setter
    def components(self, components: dict[str, object]) -> None:
        self.__components.update(components)

    @property
    def logger(self):
        return logger

    def __deserialize_notable_keys(self, **kwargs) -> dict:
        data = dict(kwargs)
        if "project_id" in data:
            data["project_id"] = deserialize(data["project_id"], EntityId)
            if hasattr(self.components, "project_service"):
                data["project"] = self.components.project_service.get_project_by_id(
                    data["project_id"]
                )
        return data

    def _on_event(self, message: ConsumerRecord) -> None:
        self.logger.error("Consumed event: %s", message)
        try:
            data = self.__deserialize_notable_keys(**message.value)
            self.on_event(message.topic, **data)
        except Exception as e:
            self.logger.error(
                "Uncaught error while processing event %s: %s", message, e
            )

    def on_event(self, topic: str, **kwargs) -> None:
        raise NotImplementedError

    def update_context(self, project: Project, *args, **kwargs):
        id = project.id
        updates = dict(kwargs)
        for i in range(0, len(args), 2):
            key = args[i]
            value = args[i + 1]
            updates[key] = value
        for key, value in updates.items():
            project = project.add_to_context(key, value)
            self.logger.info(
                "Set key %s of project %s",
                key,
                project.id,
            )
        # noinspection PyUnresolvedReferences
        self.components.project_service.update_project(id, project)

    def get_from_context(
        self, project: Project, key: str, parse_as: str
    ) -> dict | pd.DataFrame:
        setup_module = "application.automation.parsing"
        module = import_module(setup_module)
        parsing_function = getattr(module, f"parse_{parse_as}", None)
        if parsing_function is None:
            raise ValueError(
                f"Parsing function 'parse_{parse_as}' not found in module '{setup_module}'"
            )
        if hasattr(self.components, "project_service"):
            return parsing_function(
                self.components.project_service.get_from_context(project.id, key)
            )
        else:
            raise ValueError("Project service not found in components")


PACKAGE_ROOT = f"{__package__}.scripts"


def setup_consumers(events_service: EventsService, components: dict) -> None:
    scripts_path: pathlib.Path = pathlib.Path(__file__).parent / "scripts"
    script_files: Iterable[pathlib.Path] = scripts_path.glob("*.py")

    for script_file in script_files:
        module_name = script_file.name.removesuffix(".py")
        if module_name == "__init__":
            module_name = PACKAGE_ROOT
        else:
            module_name = f"{PACKAGE_ROOT}.{module_name}"
        try:
            module = import_module(module_name)
            for name in dir(module):
                if name.startswith("_") or "Abstract" in name:
                    continue
                obj = getattr(module, name)
                try:
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, Automator)
                        and obj != Automator
                    ):
                        automator = obj()
                        logger.info(
                            "Setting up an instance of class %s.%s as a consumer of topics %s",
                            module_name,
                            name,
                            automator.topics,
                        )
                    elif isinstance(obj, Automator):
                        automator = obj
                        logger.info(
                            "Setting up object %s.%s as a consumer of topics %s",
                            module_name,
                            name,
                            automator.topics,
                        )
                    else:
                        continue
                    automator.components = components
                    events_service.start_consuming(
                        list(automator.topics), automator._on_event
                    )
                except Exception as e:
                    logger.error(
                        "Error while configuring consumer %s.%s: %s",
                        module_name,
                        name,
                        e,
                    )
        except Exception as e:
            logger.error("Error while importing module %s: %s", module_name, e)

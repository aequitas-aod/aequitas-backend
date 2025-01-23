import pathlib
from importlib import import_module
import traceback

import pandas as pd
from kafka.consumer.fetcher import ConsumerRecord
from presentation.presentation import deserialize
from application.events import EventsService
from typing import Iterable, Union
from domain.common.core import EntityId
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

    def log(self, message: str, *args, level="info", **kwargs):
        logf = getattr(self.logger, level)
        logf("[%s] " + message, type(self).__name__, *args, **kwargs)

    def __deserialize_notable_keys(self, **kwargs) -> dict:
        data = dict(kwargs)
        if "project_id" in data:
            data["project_id"] = deserialize(data["project_id"], EntityId)
            if hasattr(self.components, "project_service"):
                data["project"] = self.components.project_service.get_project_by_id(
                    data["project_id"]
                )
            else:
                self.log(
                    "project_service not found in components: this may be a bug",
                    level="warning",
                )
        return data

    def _on_event(self, message: ConsumerRecord) -> None:
        self.log("Consumed event: %s", message)
        try:
            data = self.__deserialize_notable_keys(**message.value)
            self.on_event(message.topic, **data)
        except Exception as e:
            self.log(
                "Uncaught error in %s while processing event on topic %s: %s\n%s",
                type(self),
                message.topic,
                e,
                traceback.format_exc(),
                level="error",
            )

    def on_event(self, topic: str, **kwargs) -> None:
        raise NotImplementedError

    # noinspection PyUnresolvedReferences
    def update_context(self, project_id: EntityId, *args, **kwargs):
        updates = dict(kwargs)
        for i in range(0, len(args), 2):
            key = args[i]
            value = args[i + 1]
            updates[key] = value
        # FIXME: loading and storing the whole context multiple times is inefficient
        assert hasattr(
            self.components, "project_service"
        ), "project_service not found in components"
        for key, value in updates.items():
            project = self.components.project_service.get_project_by_id(project_id)
            project = project.add_to_context(key, value)
            self.components.project_service.update_project(project_id, project)
            self.log(
                "Add key %s to context of project %s. Keys are now: %s",
                key,
                project_id,
                sorted(list(project.context.keys())),
            )

    def get_from_context(
        self, project_id: EntityId, key: str, parse_as: str, optional: bool = False
    ) -> Union[dict, pd.DataFrame]:
        import application.automation.parsing as parsing

        parsing_function = getattr(parsing, f"parse_{parse_as}", None)
        if parsing_function is None:
            raise ValueError(
                f"Parsing function 'parse_{parse_as}' not found in module '{parsing.__name__}'"
            )
        if hasattr(self.components, "project_service"):
            value = self.components.project_service.get_from_context(project_id, key)[0]
            if value is None:
                if not optional:
                    self.log(
                        f"Key '%s' not found in context of project '%s'",
                        key,
                        project_id,
                        level="warning",
                    )
                return None
            try:
                return parsing_function(value)
            except Exception as e:
                raise ValueError(
                    f"Error while parsing key '{key}' of project '{project_id}'. "
                    f"Value was {value}"
                ) from e
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

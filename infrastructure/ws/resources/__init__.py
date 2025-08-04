import time


import infrastructure.ws.setup
from domain.project.factories import ProjectFactory
from infrastructure.ws.setup import events_service
from presentation.presentation import serialize
from utils.logs import logger
from typing import Iterable, Dict


_prefixes = ["pre", "in", "post"]


class EventGenerator:
    __primitive_types = (int, str, float, bool)

    def __serialize(self, obj):
        try:
            return serialize(obj)
        except ValueError as e:
            if any(isinstance(obj, t) for t in self.__primitive_types):
                return obj
            elif isinstance(obj, Dict):
                return {k: self.__serialize(v) for k, v in obj.items()}
            elif isinstance(obj, Iterable):
                return [self.__serialize(v) for v in obj]
            raise e

    @staticmethod
    def __wrap_notable_keys(**kwargs) -> Dict:
        data = dict(kwargs)
        if "project_id" in data:
            data["project_id"] = ProjectFactory.id_of(code=data["project_id"])
        return data

    def trigger_event(self, topic: str, **kwargs):
        message = self.__serialize(self.__wrap_notable_keys(**kwargs))
        if not infrastructure.ws.setup.AUTOMATION_ENABLED:
            logger.warning(
                f"Skip production of event %s, because automation is disabled. Message was:\n\t%s",
                topic,
                message,
            )
            return
        events_service.publish_message(topic, message)

    def trigger_context_event(self, event_key: str, **kwargs):
        if event_key.startswith("dataset__"):
            topic = "datasets.created"
        elif event_key.startswith("features__"):
            topic = "features.created"
        elif any(event_key.startswith(f"{prefix}processing__") for prefix in _prefixes):
            topic = "processing.requested"
            phase = event_key.split("processing__")[0]
            kwargs.update(phase=phase)
        else:
            return
        self.trigger_event(topic, **kwargs)

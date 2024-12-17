import glob
import os
from importlib import import_module
from typing import Optional

from application.events import EventsService
from application.project import ProjectService
from infrastructure.ws.utils import logger

consumers_project_service: Optional[ProjectService] = None

def setup_consumers(events_service: EventsService, project_service: ProjectService) -> None:
    scripts_path = os.path.join(os.path.dirname(__file__), "scripts")
    script_files = glob.glob(os.path.join(scripts_path, "*.py"))

    for script_file in script_files:
        module_name = os.path.splitext(os.path.basename(script_file))[0]
        module = import_module(f"application.logics.scripts.{module_name}")
        topics = getattr(module, "__topics__", [])
        on_event = getattr(module, "on_event", None)
        # on_load = getattr(module, "on_load", None)
        # if on_load:
        #     on_load(project_service=project_service)
        if on_event:
            print(f"Setting up consumer for {module_name} and topics {topics}")
            events_service.start_consuming(topics, on_event)

    # def handle_project_creation(message: Dict) -> None:
    #     project_id: dict = message["value"]["project_id"]
    #     project: Optional[Project] = project_service.get_project_by_id(deserialize(project_id, EntityId))
    #     if project is not None:
    #         project.add_to_context()
    #
    #
    # events_service.start_consuming(["projects.created"], handle_project_creation)

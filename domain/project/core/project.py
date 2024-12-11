from copy import deepcopy
from typing import Any, Dict, Optional

from pydantic import BaseModel

from domain.common.core import EntityId
from utils.encodings import encode, decode


class Project(BaseModel):

    id: EntityId
    name: str
    context: Optional[Dict[str, str]] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.context is None:
            self.context = {}

    def get_context(self) -> Dict[str, str]:
        """Returns the decoded context"""
        return {k: decode(v) for k, v in self.context.items()}

    def add_to_context(self, key: str, value: str) -> "Project":
        """
        Add a key-value pair to the context. The value is encoded before adding it to the context.
        :param key: The key to add
        :param value: The value to add
        :return: A new instance of the project with the key-value pair added to the context
        """
        if key in self.context:
            raise ValueError(f"Key {key} already exists in context")
        new_project = deepcopy(self)
        new_project.context[key] = encode(value)
        return new_project

    def get_from_context(self, key: str) -> str:
        """
        Get a value from the context by key. The value is decoded before returning it.
        :param key: The key to get the value for
        """
        if key not in self.context:
            raise ValueError(f"Key {key} does not exist in context")
        return decode(self.context[key])

    def remove_from_context(self, key: str) -> "Project":
        """
        Remove a key from the context.
        :param key: The key of the key-value pair to remove
        :return: A new instance of the project with the key removed from the context
        """
        if key not in self.context:
            raise ValueError(f"Key {key} does not exist in context")
        new_project = deepcopy(self)
        new_project.context.pop(key)
        return new_project

    def __str__(self) -> str:
        return f"Project(id={self.id}, name={self.name}, context={self.context})"

    def __hash__(self):
        return hash((self.id, self.name, tuple(self.context.items())))

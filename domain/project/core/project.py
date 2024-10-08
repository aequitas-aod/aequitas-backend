from copy import deepcopy

from pydantic import BaseModel

from domain.project.core import ProjectId


class Project(BaseModel):

    id: ProjectId
    name: str
    context: dict[str, str]

    def add_to_context(self, key: str, value: str) -> "Project":
        if key in self.context:
            raise ValueError(f"Key {key} already exists in context")
        return Project(id=self.id, name=self.name, context={**self.context, key: value})

    def remove_from_context(self, key: str) -> "Project":
        if key not in self.context:
            raise ValueError(f"Key {key} does not exist in context")
        context: dict[str, str] = deepcopy(self.context)
        context.pop(key)
        return Project(id=self.id, name=self.name, context=context)

    def __str__(self) -> str:
        return f"Project(id={self.id}, name={self.name}, context={self.context})"

    def __hash__(self):
        return hash(self.id.code)

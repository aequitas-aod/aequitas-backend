from domain.common.core import EntityId
from domain.project.core import Project


class ProjectFactory:

    @staticmethod
    def id_of(code: str) -> EntityId:
        return EntityId(code=code)

    @staticmethod
    def create_project(
        project_id: EntityId, name: str, context: dict[str, str]
    ) -> Project:
        return Project(id=project_id, name=name, context=context)

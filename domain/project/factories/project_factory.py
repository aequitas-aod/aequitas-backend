from domain.project.core import Project, ProjectId


class ProjectFactory:

    @staticmethod
    def create_project(
        project_id: ProjectId, name: str, context: dict[str, str]
    ) -> Project:
        return Project(id=project_id, name=name, context=context)

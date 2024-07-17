from typing import List, Optional

from domain.project.core import ProjectId, Project
from domain.project.factories import ProjectFactory
from domain.project.repositories.project_repository import ProjectRepository
from presentation.presentation import deserialize, serialize
from utils.env import DB_HOST, DB_USER, DB_PASSWORD
from utils.errors import NotFoundError, ConflictError
from utils.neo4j_driver import Neo4jDriver, Credentials, Neo4jQuery


class Neo4jProjectRepository(ProjectRepository):

    def __init__(self):
        self.driver: Neo4jDriver = Neo4jDriver(
            DB_HOST, Credentials(DB_USER, DB_PASSWORD)
        )

    def get_all_projects(self) -> List[Project]:
        query_string: str = "MATCH (p:Project) RETURN p"
        query: Neo4jQuery = Neo4jQuery(query_string, {})
        res: List[dict] = self.driver.query(query)
        projects: List[Project] = []
        for r in res:
            project: Project = self._convert_node_in_project(r["p"])
            projects.append(project)
        return projects

    def get_project_by_id(self, project_id: ProjectId) -> Optional[Project]:
        query_string: str = "MATCH (p:Project {id: $project_id}) RETURN p"
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_id": project_id.code})
        r: List[dict] = self.driver.query(query)
        if len(r) == 0:
            return None
        project: Project = self._convert_node_in_project(r[0]["p"])
        return project

    def insert_project(self, project: Project) -> ProjectId:
        if self._check_project_exists(project.id):
            raise ConflictError(f"Project with id {project.id} already exists")

        p: dict = self._convert_project_in_node(project)
        self.driver.query(
            Neo4jQuery(
                "CREATE (:Project $project)",
                {"project": p},
            )
        )
        return project.id

    def update_project(self, project_id: ProjectId, project: Project) -> None:
        if not self._check_project_exists(project_id):
            raise NotFoundError(f"Project with id {project_id} does not exist")
        self.delete_project(project_id)
        self.insert_project(project)

    def delete_project(self, project_id: ProjectId) -> None:
        if not self._check_project_exists(project_id):
            raise NotFoundError(f"Project with id {project_id} does not exist")
        query_string = (
            "MATCH path = (p:Project {id: $project_code})-[*]-(nodeToDelete) "
            "WITH nodes(path) AS nodesToDelete "
            "UNWIND nodesToDelete AS node "
            "DETACH DELETE node"
        )
        self.driver.query(
            Neo4jQuery(
                query_string,
                {"project_code": project_id.code},
            )
        )

    def _check_project_exists(self, project_id: ProjectId) -> bool:
        p: Project = self.get_project_by_id(project_id)
        return p is not None

    def _convert_project_in_node(self, project: Project) -> dict:
        p: dict = serialize(project)
        p["id"] = project.id.code
        return p

    def _convert_node_in_project(self, p: dict) -> Project:
        project: dict = p
        project["id"] = {"code": project["id"]}
        project["name"] = project["name"]
        return deserialize(project, Project)


if __name__ == "__main__":
    Neo4jProjectRepository().delete_project(ProjectId(code="p1"))
    p1: Project = ProjectFactory.create_project(ProjectId(code="p1"), "Project 1")
    Neo4jProjectRepository().insert_project(p1)

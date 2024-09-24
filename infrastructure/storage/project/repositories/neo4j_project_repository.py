from typing import List, Optional

from domain.project.core import ProjectId, Project
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
        query_string: str = ("MATCH (p:Project) "
                             "MATCH (p)-[:HAS_CONTEXT]->(pc:ProjectContext) "
                             "RETURN p, pc")
        query: Neo4jQuery = Neo4jQuery(query_string, {})
        res: List[dict] = self.driver.query(query)
        projects: List[Project] = []
        for r in res:
            project: Project = self._convert_node_in_project(r["p"], r["pc"])
            projects.append(project)
        return projects

    def get_project_by_id(self, project_id: ProjectId) -> Optional[Project]:
        query_string: str = ("MATCH (p:Project {id: $project_id}) "
                             "OPTIONAL MATCH (p)-[:HAS_CONTEXT]->(pc:ProjectContext) "
                             "RETURN p, pc")
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_id": project_id.code})
        r: List[dict] = self.driver.query(query)
        if len(r) == 0:
            return None
        project: Project = self._convert_node_in_project(r[0]["p"], r[0]["pc"])
        return project

    def insert_project(self, project: Project) -> ProjectId:
        if self._check_project_exists(project.id):
            raise ConflictError(f"Project with id {project.id} already exists")

        context: dict[str, str] = {}
        for key in project.context:
            context[key] = project.context[key]
        p: dict = self._convert_project_in_node(project)
        self.driver.query(
            Neo4jQuery(
                "CREATE (p: Project $project) "
                "CREATE (pc: ProjectContext $context) "
                "CREATE (p)-[:HAS_CONTEXT]->(pc)",
                {"project": p, "context": context},
            )
        )
        return project.id

    def update_project(self, project_id: ProjectId, project: Project) -> None:
        if not self._check_project_exists(project_id):
            raise NotFoundError(f"Project with id {project_id} does not exist")
        if project_id != project.id:
            raise ConflictError("Updated project id does not match")
        p: dict = self._convert_project_in_node(project)
        self.driver.query(
            Neo4jQuery(
                "MATCH (p:Project {id: $project_code}) SET p = $project",
                {"project_code": project_id.code, "project": p},
            )
        )

    def delete_project(self, project_id: ProjectId) -> None:
        if not self._check_project_exists(project_id):
            raise NotFoundError(f"Project with id {project_id} does not exist")
        query_string = (
            "MATCH (p:Project {id: $project_code}) "
            "OPTIONAL MATCH path = (p)-[*]-(nodeToDelete) "
            "DETACH DELETE nodeToDelete, p"
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
        del p["context"]
        return p

    def _convert_node_in_project(self, p: dict, pc: Optional[dict]) -> Project:
        project: dict = p
        project["id"] = {"code": project["id"]}
        project["name"] = project["name"]
        project["context"] = {} if pc is None else pc
        return deserialize(project, Project)

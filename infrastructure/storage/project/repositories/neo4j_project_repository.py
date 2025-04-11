from typing import List, Optional, Dict

from domain.common.core import EntityId
from domain.project.core import Project
from domain.project.repositories.project_repository import ProjectRepository
from infrastructure.storage import db_log
from presentation.presentation import deserialize, serialize
from utils.encodings import decode
from utils.env import DB_HOST, DB_USER, DB_PASSWORD
from utils.errors import NotFoundError, ConflictError
from utils.neo4j_driver import Neo4jDriver, Credentials, Neo4jQuery


class Neo4jProjectRepository(ProjectRepository):

    def __init__(self):
        self.driver: Neo4jDriver = Neo4jDriver(
            DB_HOST, Credentials(DB_USER, DB_PASSWORD)
        )
        db_log("Configure driver to connect to %s, with user %s", DB_HOST, DB_USER)

    def get_all_projects(self) -> List[Project]:
        query_string: str = (
            "MATCH (p:Project) "
            "MATCH (p)-[:HAS_CONTEXT]->(pc:ProjectContext) "
            "RETURN p, pc"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {})
        res: List[Dict] = self.driver.query(query)
        projects: List[Project] = []
        for r in res:
            project: Project = self._convert_node_in_project(r["p"], r["pc"])
            projects.append(project)
        db_log(
            "Retrieved %s projects: %s",
            len(projects),
            [project.id.code for project in projects],
        )
        return projects

    def get_project_by_id(self, project_id: EntityId) -> Optional[Project]:
        query_string: str = (
            "MATCH (p:Project {code: $project_code}) "
            "OPTIONAL MATCH (p)-[:HAS_CONTEXT]->(pc:ProjectContext) "
            "RETURN p, pc"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_code": project_id.code})
        r: List[Dict] = self.driver.query(query)
        if len(r) == 0:
            return None
        project: Project = self._convert_node_in_project(r[0]["p"], r[0]["pc"])
        db_log(
            "Retrieved project %s: Context contains key: %s.",
            project.id.code,
            sorted(list(project.context.keys())),
        )
        return project

    def insert_project(self, project: Project) -> EntityId:
        if self.check_project_exists(project.id):
            raise ConflictError(f"Project with id {project.id} already exists")

        context: Dict = self._get_context_dict(project)
        p: Dict = self._convert_project_in_node(project)
        self.driver.query(
            Neo4jQuery(
                "CREATE (p: Project $project) "
                "CREATE (pc: ProjectContext $context) "
                "CREATE (p)-[:HAS_CONTEXT]->(pc)",
                {"project": p, "context": context},
            )
        )
        db_log(
            "Inserted project with id %s. Context contains keys: %s",
            project.id.code,
            sorted(list(context.keys())),
        )
        return project.id

    def update_project(self, project_id: EntityId, project: Project) -> None:
        if not self.check_project_exists(project_id):
            raise NotFoundError(f"Project with id {project_id} does not exist")
        if project_id != project.id:
            raise ConflictError("Updated project id does not match")
        p: Dict = self._convert_project_in_node(project)
        context: Dict = self._get_context_dict(project)
        query = (
            "MATCH (p:Project {code: $project_code}) "
            "OPTIONAL MATCH (p)-[r:HAS_CONTEXT]->(pc:ProjectContext) "
            "SET p = $project "
            "SET pc = $context"
        )
        self.driver.query(
            Neo4jQuery(
                query,
                {"project_code": project_id.code, "project": p, "context": context},
            )
        )
        db_log(
            "Updated project with id %s. New context contains keys: %s",
            project.id.code,
            sorted(list(context.keys())),
        )

    def delete_project(self, project_id: EntityId) -> None:
        if not self.check_project_exists(project_id):
            raise NotFoundError(f"Project with id {project_id} does not exist")
        query_string = (
            "MATCH (p:Project {code: $project_code}) "
            "OPTIONAL MATCH path = (p)-[*]-(nodeToDelete) "
            "DETACH DELETE nodeToDelete, p"
        )
        self.driver.query(
            Neo4jQuery(
                query_string,
                {"project_code": project_id.code},
            )
        )
        db_log("Deleted project with id %s", project_id.code)

    def get_public_context(self) -> dict:
        query_string: str = "MATCH (p:PublicContext) RETURN p"
        query: Neo4jQuery = Neo4jQuery(query_string, {})
        res: List[Dict] = self.driver.query(query)
        if len(res) == 0:
            return {}
        context: Dict[str, str] = res[0]["p"]
        result = {key: decode(value) for key, value in context.items()}
        db_log(
            "Retrieved public context. It contains the following keys %s",
            sorted(list(result.keys())),
        )
        return result

    def add_context_key(self, project_id: EntityId, key: str, value: str) -> None:
        if not self.check_project_exists(project_id):
            raise NotFoundError(f"Project with id {project_id} does not exist")
        query_string: str = (
            "MATCH (p:Project {code: $project_code})-[:HAS_CONTEXT]->(pc:ProjectContext) "
            "CALL apoc.create.setProperty(pc, $key, $value) "
            "YIELD node RETURN node"
        )
        query: Neo4jQuery = Neo4jQuery(
            query_string, {"project_code": project_id.code, "key": key, "value": value}
        )
        self.driver.query(query)
        db_log("Added key %s to project with id %s", key, project_id.code)

    def check_project_exists(self, project_id: EntityId) -> bool:
        query_string: str = "MATCH (p:Project {code: $project_code}) RETURN count(p) > 0 as exists"
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_code": project_id.code})
        res: List[Dict] = self.driver.query(query)
        return res[0]["exists"]

    def _convert_project_in_node(self, project: Project) -> Dict:
        p: Dict = serialize(project)
        del p["id"]
        p["code"] = project.id.code
        del p["context"]
        return p

    def _convert_node_in_project(self, p: Dict, pc: Optional[Dict]) -> Project:
        project: Dict = p
        project["id"] = {"code": project["code"]}
        project["name"] = project["name"]
        project["context"] = {} if pc is None else pc
        return deserialize(project, Project)

    def _get_context_dict(self, project: Project) -> Dict:
        context: Dict[str, str] = {}
        for key in project.context:
            context[key] = project.context[key]
        return context

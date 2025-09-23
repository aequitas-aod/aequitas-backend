from typing import List, Optional

from domain.common.core import EntityId
from domain.graph.repositories import GraphQuestionRepository
from domain.project.core import (
    ProjectQuestion,
    Project,
    ProjectAnswer,
)
from domain.project.factories import ProjectFactory, ProjectQuestionFactory
from domain.project.repositories import ProjectRepository
from domain.project.repositories.questionnaire_repository import QuestionnaireRepository
from infrastructure.storage.graph.repositories import Neo4JGraphQuestionRepository
from infrastructure.storage.project.repositories.neo4j_project_repository import (
    Neo4jProjectRepository,
)
from presentation.presentation import serialize, deserialize
from utils.env import DB_HOST, DB_USER, DB_PASSWORD
from utils.errors import NotFoundError, BadRequestError, MissingFirstQuestion
from utils.neo4j_driver import Neo4jDriver, Credentials, Neo4jQuery


class Neo4jQuestionnaireRepository(QuestionnaireRepository):

    def __init__(self):
        self.driver: Neo4jDriver = Neo4jDriver(
            DB_HOST, Credentials(DB_USER, DB_PASSWORD)
        )
        self.project_repository: ProjectRepository = Neo4jProjectRepository()
        self.graph_question_repository: GraphQuestionRepository = (
            Neo4JGraphQuestionRepository()
        )

    def get_nth_question(self, project_id: EntityId, index: int) -> ProjectQuestion:
        if index <= 0:
            raise ValueError("Index must be greater than 0")
        elif index == 1:
            query_string: str = (
                "MATCH (p:Project {code: $project_code})-[:QUESTIONNAIRE]->(q:ProjectQuestion) "
                "OPTIONAL MATCH (q)-[:HAS_AVAILABLE]->(available:ProjectAnswer) "
                "OPTIONAL MATCH (q)-[:HAS_SELECTED]->(selected:ProjectAnswer) "
                "RETURN q, COLLECT(available) AS available_answers, COLLECT(selected) AS selected_answers, p AS project"
            )
            query: Neo4jQuery = Neo4jQuery(
                query_string, {"project_code": project_id.code}
            )
            res: List[dict] = self.driver.query(query)
            if len(res) == 0:
                raise MissingFirstQuestion()

            question: ProjectQuestion = self._convert_node_in_project_question(
                res[0]["q"],
                res[0]["available_answers"],
                res[0]["selected_answers"],
                res[0]["project"]["code"],
            )
            return question
        else:
            question_index: int = index - 1
            query_string: str = (
                "MATCH (p:Project {code: $project_code})-[:QUESTIONNAIRE]->(initial:ProjectQuestion) "
                f"MATCH path = (initial)-[:NEXT*{question_index}]->(:ProjectQuestion) "
                "WITH nodes(path) AS questions  "
                f"WITH questions[{question_index}] as q, questions[{question_index}-1] as prev_q "
                "OPTIONAL MATCH (q)-[:HAS_AVAILABLE]->(available:ProjectAnswer)  "
                "OPTIONAL MATCH (q)-[:HAS_SELECTED]->(selected:ProjectAnswer)  "
                "RETURN q, COLLECT(available) AS available_answers, COLLECT(selected) AS selected_answers, prev_q"
            )
            query: Neo4jQuery = Neo4jQuery(
                query_string, {"project_code": project_id.code}
            )
            res: List[dict] = self.driver.query(query)
            if len(res) == 0:
                try:
                    previous_question: ProjectQuestion = self.get_nth_question(
                        project_id, index - 1
                    )
                    previous_answers_selected: List[EntityId] = [
                        a.id for a in previous_question.answers if a.selected
                    ]
                    enabled_question = (
                        self.graph_question_repository.get_enabled_question(
                            previous_question.id, previous_answers_selected
                        )
                    )
                except Exception:
                    raise NotFoundError("Question not found")

                if enabled_question is None:
                    raise BadRequestError("Questionnaire is finished")
                else:
                    raise NotFoundError("Question not found")

            question: ProjectQuestion = self._convert_node_in_project_question(
                res[0]["q"],
                res[0]["available_answers"],
                res[0]["selected_answers"],
                project_id.code,
            )
            return question

    def get_last_question(self, project_id: EntityId) -> Optional[ProjectQuestion]:
        query_string: str = (
            "MATCH (p:Project {code: $project_code})-[:QUESTIONNAIRE]->(initial:ProjectQuestion) "
            "MATCH path = (initial)-[:NEXT*0..]->(:ProjectQuestion) "
            "WITH nodes(path) AS questions "
            "RETURN questions[-1] AS q"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_code": project_id.code})
        res: List[dict] = self.driver.query(query)
        if len(res) == 0:
            return None
        question: ProjectQuestion = self.get_project_question_by_id(
            ProjectQuestionFactory.id_of(
                code=res[-1]["q"]["code"], project_id=project_id
            )
        )
        return question

    def get_project_question_by_id(
        self, project_question_id: EntityId
    ) -> Optional[ProjectQuestion]:
        project_code: str = project_question_id.project_code
        query_string: str = (
            "MATCH (p:Project {code: $project_code}) "
            "MATCH (q:ProjectQuestion {code: $question_code}) "
            "MATCH path = (p)-[:QUESTIONNAIRE|NEXT*]->(q) "
            "OPTIONAL MATCH (q)-[:HAS_AVAILABLE]->(available:ProjectAnswer) "
            "OPTIONAL MATCH (q)-[:HAS_SELECTED]->(selected:ProjectAnswer) "
            "OPTIONAL MATCH (prev_q: ProjectQuestion)-[:NEXT]->(q) "
            "RETURN q, COLLECT(available) AS available_answers, COLLECT(selected) AS selected_answers, prev_q"
        )
        query: Neo4jQuery = Neo4jQuery(
            query_string,
            {"project_code": project_code, "question_code": project_question_id.code},
        )
        res: List[dict] = self.driver.query(query)
        if len(res) == 0:
            return None
        question: ProjectQuestion = self._convert_node_in_project_question(
            res[0]["q"],
            res[0]["available_answers"],
            res[0]["selected_answers"],
            project_code,
        )
        return question

    def insert_project_question(self, question: ProjectQuestion) -> EntityId:
        project_id: EntityId = ProjectFactory.id_of(code=question.id.project_code)
        project: Optional[Project] = self.project_repository.get_project_by_id(
            project_id
        )
        if project is None:
            raise ValueError(f"Project with id {project_id} does not exist")
        queries: List[Neo4jQuery] = []
        # if question with the same code already exists, add a suffix to the code
        already_exists: bool = self._check_project_question_exists_within_project(
            question.id
        )
        # save code without suffix in the question text for graph question reference
        question_code_without_suffix: str = question.id.code

        if already_exists:
            question.id.code = f"{question.id.code}-2"
            already_exists = self._check_project_question_exists_within_project(
                question.id
            )
            if already_exists:
                res = self.driver.query(
                    Neo4jQuery(
                        "MATCH (q:ProjectQuestion) "
                        "MATCH (p:Project {code: $project_code}) "
                        "MATCH path = (p)-[:QUESTIONNAIRE|NEXT*]->(q) "
                        "WHERE q.code STARTS WITH $question_code "
                        "WITH q, toInteger(REPLACE(q.code, $question_code, '')) AS codeNum "
                        "ORDER BY codeNum DESC "
                        "LIMIT 1 "
                        "RETURN q, codeNum ",
                        {
                            "project_code": project_id.code,
                            "question_code": question_code_without_suffix + "-",
                        },
                    )
                )
                suffix = res[0]["codeNum"] + 1
                question.id.code = f"{question_code_without_suffix}-{suffix}"

        q: dict = self._convert_project_question_in_node(question)
        query_string: str = (
            "CREATE (q:ProjectQuestion $question) RETURN elementId(q) AS node_question_id"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {"question": q})
        queries.append(query)

        res = self.driver.query(
            Neo4jQuery(
                "MATCH (q:GraphQuestion {code: $question_code_without_suffix})-[:ENABLED_BY]->(a:GraphAnswer)<-[:HAS_ANSWER]-(prev_q:GraphQuestion) "
                "RETURN prev_q.code AS previous_question_code ",
                {"question_code_without_suffix": question_code_without_suffix},
            )
        )
        if len(res) == 0:
            query_string: str = (
                "MATCH (p:Project {code: $project_code}) "
                "MATCH (q:ProjectQuestion {code: $question_code}) "
                "WHERE elementId(q) = $node_question_id "
                "CREATE (p)-[:QUESTIONNAIRE]->(q)"
            )
            query: Neo4jQuery = Neo4jQuery(
                query_string,
                {"project_code": project_id.code, "question_code": question.id.code},
            )
            queries.append(query)
        else:
            last_project_question: Optional[ProjectQuestion] = self.get_last_question(
                project_id
            )
            if last_project_question:
                query_string: str = (
                    "MATCH (project_q:ProjectQuestion {code: $question_code}) "
                    "WHERE elementId(project_q) = $node_question_id "
                    "MATCH (project_prev_q:ProjectQuestion {code: $last_question_code}) "
                    "MATCH (p:Project {code: $project_code}) "
                    "MATCH path = (p)-[:QUESTIONNAIRE|NEXT*]->(project_prev_q) "
                    "MERGE (project_prev_q)-[:NEXT]->(project_q)"
                )
                query: Neo4jQuery = Neo4jQuery(
                    query_string,
                    {
                        "project_code": project_id.code,
                        "question_code": question.id.code,
                        "last_question_code": last_project_question.id.code,
                    },
                )
                # query_string: str = (
                #     "MATCH (project_q:ProjectQuestion {code: $question_code}) "
                #     "WHERE elementId(project_q) = $node_question_id "
                #     "MATCH (graph_q:GraphQuestion {code: $question_code_without_suffix})-[:ENABLED_BY]->(a:GraphAnswer)<-[:HAS_ANSWER]-(graph_prev_q:GraphQuestion) "
                #     "MATCH (project_answer:ProjectAnswer {code: a.code})<-[:HAS_SELECTED]-(project_prev_q:ProjectQuestion {code: graph_prev_q.code}) "
                #     "MATCH (p:Project {code: $project_code})-[*]-(project_prev_q) "
                #     "MERGE (project_prev_q)-[:NEXT]->(project_q)"
                # )
                # query: Neo4jQuery = Neo4jQuery(
                #     query_string,
                #     {"project_code": project_id.code, "question_code": question.id.code, "question_code_without_suffix": question_code_without_suffix},
                # )
                queries.append(query)

        for answer in question.answers:
            a: dict = self._convert_answer_in_node(answer)
            queries.append(Neo4jQuery("CREATE (:ProjectAnswer $answer)", {"answer": a}))
            queries.append(
                Neo4jQuery(
                    "MATCH (q:ProjectQuestion {code: $question_code}) "
                    "WHERE elementId(q) = $node_question_id "
                    "MATCH (a:ProjectAnswer {code: $answer_code}) "
                    "WHERE NOT (a)--() "  # selecting answers that are not connected any other node (nodes just created)
                    f"CREATE (q)-[:HAS_AVAILABLE]->(a) "
                    f"{'CREATE (q)-[:HAS_SELECTED]->(a)' if answer.selected else ''} "
                    "RETURN a",
                    {
                        "question_code": question.id.code,
                        "answer_code": answer.id.code,
                    },
                )
            )

        self.driver.transaction(queries)
        return question.id

    def update_project_question(
        self, question_id: EntityId, question: ProjectQuestion
    ) -> None:
        if not self._check_project_question_exists_within_project(question_id):
            raise NotFoundError(f"Question with id {question_id} does not exist")
        new_project_question: dict = self._convert_project_question_in_node(question)
        queries: List[Neo4jQuery] = []
        query = """
                MATCH (q:ProjectQuestion {code: $question_code})
                MATCH (p:Project {code: $project_code})
                MATCH path = (p)-[:QUESTIONNAIRE|NEXT*]->(q)
                SET q.text = $text,
                    q.description = $description,
                    q.type = $type,
                    q.selection_strategy = $selection_strategy
                RETURN elementId(q) AS node_question_id
                """

        queries.append(
            Neo4jQuery(
                query,
                {
                    "project_code": question_id.project_code,
                    "question_code": question_id.code,
                    "text": new_project_question["text"],
                    "description": new_project_question["description"],
                    "type": new_project_question["type"],
                    "selection_strategy": new_project_question["selection_strategy"],
                },
            )
        )
        queries.append(
            Neo4jQuery(
                "MATCH (q:ProjectQuestion {code: $question_code})-[:HAS_AVAILABLE|:HAS_SELECTED]->(a:ProjectAnswer) "
                "WHERE elementId(q) = $node_question_id "
                "DETACH DELETE a",
                {"question_code": question_id.code},
            )
        )

        for answer in question.answers:
            a: dict = self._convert_answer_in_node(answer)
            queries.append(Neo4jQuery("CREATE (:ProjectAnswer $answer)", {"answer": a}))
            queries.append(
                Neo4jQuery(
                    "MATCH (q:ProjectQuestion {code: $question_code}) "
                    "WHERE elementId(q) = $node_question_id "
                    "MATCH (a:ProjectAnswer {code: $answer_code}) "
                    "WHERE NOT (a)--() "  # selecting answers that are not connected any other node (nodes just created)
                    f"CREATE (q)-[:HAS_AVAILABLE]->(a) "
                    f"{'CREATE (q)-[:HAS_SELECTED]->(a)' if answer.selected else ''} ",
                    {
                        "question_code": question.id.code,
                        "answer_code": answer.id.code,
                    },
                )
            )
        self.driver.transaction(queries)

    def delete_project_question(self, question_id: EntityId) -> None:
        if not self._check_project_question_exists_within_project(question_id):
            raise NotFoundError(f"Question with id {question_id} does not exist")
        self.driver.query(
            Neo4jQuery(
                "MATCH (p:Project {code: $project_code})-[*]-(q:ProjectQuestion {code: $question_code}) "
                "WITH DISTINCT q "
                "OPTIONAL MATCH (q)-[]->(a:ProjectAnswer) "
                "DETACH DELETE q, a",
                {
                    "project_code": question_id.project_code,
                    "question_code": question_id.code,
                },
            )
        )

    def get_questionnaire(self, project_id: EntityId) -> List[ProjectQuestion]:
        query_string: str = (
            "MATCH (p:Project {code: $project_code})-[:QUESTIONNAIRE]->(initial:ProjectQuestion) "
            "MATCH path = (initial)-[:NEXT*0..]->(:ProjectQuestion) "
            "WITH nodes(path) AS questions "
            "RETURN questions[-1] as q"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_code": project_id.code})
        res: List[dict] = self.driver.query(query)
        questions: List[ProjectQuestion] = []
        for q in res:
            question: ProjectQuestion = self.get_project_question_by_id(
                ProjectQuestionFactory.id_of(code=q["q"]["code"], project_id=project_id)
            )
            questions.append(question)
        return questions

    def delete_questionnaire(self, project_id: EntityId):
        query_string = (
            "CALL {"
            "    OPTIONAL MATCH (p:Project {code: $project_code})-[:QUESTIONNAIRE]->(initial:ProjectQuestion)"
            "    OPTIONAL MATCH (initial)-[*]->(nodeToDelete)"
            "    WITH nodeToDelete, initial LIMIT 1000"
            "    DETACH DELETE initial, nodeToDelete"
            "}"
        )
        self.driver.query(
            Neo4jQuery(
                query_string,
                {"project_code": project_id.code},
            )
        )
        self.driver.query(
            Neo4jQuery(
                "MATCH (p:Project {code: $project_code})-[:HAS_CONTEXT]->(c:ProjectContext) SET c = {}",
                {"project_code": project_id.code},
            )
        )

    def _check_project_question_exists_within_project(
        self, question_id: EntityId
    ) -> bool:
        q: ProjectQuestion = self.get_project_question_by_id(question_id)
        return q is not None

    def _convert_project_question_in_node(self, question: ProjectQuestion) -> dict:
        q: dict = serialize(question)
        del q["id"]
        q["code"] = question.id.code
        q["created_at"] = question.created_at.isoformat()
        q["selection_strategy"] = question.selection_strategy.__class__.__name__
        del q["answers"]
        return q

    def _convert_answer_in_node(self, answer: ProjectAnswer) -> dict:
        a: dict = serialize(answer)
        del a["id"]
        a["code"] = answer.id.code
        del a["selected"]
        return a

    def _convert_node_in_project_question(
        self,
        q: dict,
        available_answers: List,
        selected_answers: List,
        project_code: str,
    ) -> ProjectQuestion:
        question: dict = q
        question["id"] = {"code": q["code"], "project_code": project_code}
        del question["code"]
        question["description"] = q["description"] if "description" in q else None
        question["selection_strategy"] = {"type": q["selection_strategy"]}
        question["answers"] = [
            {
                "id": {
                    "code": a["code"],
                    "question_code": question["id"]["code"],
                    "project_code": project_code,
                },
                "text": a["text"],
                "description": a["description"] if "description" in a else None,
                "selected": a in selected_answers,
            }
            for a in available_answers + selected_answers
        ]
        return deserialize(question, ProjectQuestion)

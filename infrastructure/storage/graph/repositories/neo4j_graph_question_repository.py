from typing import List, Optional

from domain.common.core import Answer, EntityId
from domain.common.factories import AnswerFactory
from domain.graph.core import GraphQuestion
from domain.graph.factories import GraphQuestionFactory
from domain.graph.repositories import GraphQuestionRepository
from presentation.presentation import serialize, deserialize
from utils.env import DB_HOST, DB_USER, DB_PASSWORD
from utils.errors import NotFoundError, ConflictError
from utils.neo4j_driver import Neo4jDriver, Credentials, Neo4jQuery


class Neo4JGraphQuestionRepository(GraphQuestionRepository):

    def __init__(self):
        self.driver: Neo4jDriver = Neo4jDriver(
            DB_HOST, Credentials(DB_USER, DB_PASSWORD)
        )

    def get_all_questions(self) -> List[GraphQuestion]:
        query_string = (
            "MATCH (q:GraphQuestion)-[:HAS_ANSWER]->(a:Answer) "
            "OPTIONAL MATCH (q)-[:PREVIOUS]->(prev:GraphQuestion) "
            "RETURN q, COLLECT(a) AS answers"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {})
        res: List[dict] = self.driver.query(query)
        questions: List[GraphQuestion] = []
        for r in res:
            question: GraphQuestion = self._convert_node_in_question(
                r["q"], r["answers"]
            )
            questions.append(question)
        return questions

    def get_question_by_id(self, question_id: EntityId) -> Optional[GraphQuestion]:
        query_string = (
            "MATCH (q:GraphQuestion {code: $question_code})-[:HAS_ANSWER]->(a:Answer) "
            "OPTIONAL MATCH (q)-[:PREVIOUS]->(prev:GraphQuestion) "
            "RETURN q, COLLECT(a) AS answers"
        )
        query: Neo4jQuery = Neo4jQuery(
            query_string, {"question_code": question_id.code}
        )
        r: List[dict] = self.driver.query(query)
        if len(r) == 0:
            return None
        question: GraphQuestion = self._convert_node_in_question(
            r[0]["q"], r[0]["answers"]
        )
        return question

    def insert_question(self, question: GraphQuestion) -> None:
        if self._check_question_exists(question.id):
            raise ConflictError(f"Question with id {question.id} already exists")

        q: dict = self._convert_question_in_node(question)
        queries: List[Neo4jQuery] = [
            Neo4jQuery(
                "CREATE (:GraphQuestion $question)",
                {"question": q},
            )
        ]
        for answer in question.answers:
            if self._check_answer_exists(answer.id):
                self.update_answer(answer.id, answer)
            else:
                self.insert_answer(answer)
            queries.append(
                Neo4jQuery(
                    "MATCH (q:GraphQuestion {code: $question_code}) "
                    "MATCH (a:Answer {code: $answer_code}) "
                    "CREATE (q)-[:HAS_ANSWER]->(a)",
                    {"question_code": question.id.code, "answer_code": answer.id.code},
                )
            )
        for answer_id in question.enabled_by:
            if not self._check_answer_exists(answer_id):
                self.insert_answer(AnswerFactory.create_answer(answer_id, ""))
            queries.append(
                Neo4jQuery(
                    "MATCH (q1:GraphQuestion {code: $question_code}) "
                    "MATCH (a:Answer {code: $answer_code}) "
                    "CREATE (q1)-[:ENABLED_BY]->(a)",
                    {"question_code": question.id.code, "answer_code": answer_id.code},
                )
            )

        self.driver.transaction(queries)

    def insert_answer(self, answer: Answer) -> None:
        if self._check_answer_exists(answer.id):
            raise ConflictError(f"Answer with id {answer.id} already exists")
        a: dict = self._convert_answer_in_node(answer)
        query: Neo4jQuery = Neo4jQuery("CREATE (:Answer $answer)", {"answer": a})
        self.driver.query(query)

    def update_question(self, question_id: EntityId, question: GraphQuestion) -> None:
        if not self._check_question_exists(question_id):
            raise NotFoundError(f"Question with id {question_id} does not exist")
        self.delete_question(question_id)
        self.insert_question(question)

    def update_answer(self, answer_id: EntityId, answer: Answer) -> None:
        if not self._check_answer_exists(answer_id):
            raise NotFoundError(f"Answer with id {answer_id} does not exist")
        a: dict = self._convert_answer_in_node(answer)
        query: Neo4jQuery = Neo4jQuery(
            "MATCH (a:Answer {code: $answer_code}) SET a = $answer",
            {"answer_code": answer_id.code, "answer": a},
        )
        self.driver.query(query)

    def delete_question(self, question_id: EntityId) -> None:
        if not self._check_question_exists(question_id):
            raise NotFoundError(f"Question with id {question_id} does not exist")
        self.driver.query(
            Neo4jQuery(
                "MATCH (q:GraphQuestion {code: $question_code})-[:HAS_ANSWER]->(a:Answer) "
                "DETACH DELETE q, a",
                {"question_code": question_id.code},
            )
        )

    def delete_answer(self, answer_id: EntityId) -> None:
        if not self._check_answer_exists(answer_id):
            raise NotFoundError(f"Answer with id {answer_id} does not exist")
        self.driver.query(
            Neo4jQuery(
                "MATCH (a:Answer {code: $answer_code}) " "DETACH DELETE a",
                {"answer_code": answer_id.code},
            )
        )

    def get_last_inserted_question(self) -> Optional[GraphQuestion]:
        query_string = (
            "MATCH (q:GraphQuestion)-[:HAS_ANSWER]->(a:Answer) "
            "OPTIONAL MATCH (q)-[:PREVIOUS]->(prev:GraphQuestion) "
            "RETURN q, COLLECT(a) AS answers "
            "ORDER BY q.created_at DESC LIMIT 1"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {})
        r: List[dict] = self.driver.query(query)
        if len(r) == 0:
            return None
        question: GraphQuestion = self._convert_node_in_question(
            r[0]["q"], r[0]["answers"]
        )
        return question

    def get_enabled_question(
        self, question_id: EntityId, answer_ids: List[EntityId]
    ) -> Optional[GraphQuestion]:
        query_string = (
            "MATCH (q:GraphQuestion {code: $question_code})-[:HAS_ANSWER]->(a:Answer) "
            "WHERE a.code IN $answer_codes "
            "MATCH (q_enabled:GraphQuestion)-[:ENABLED_BY]->(a:Answer) "
            "MATCH (q_enabled)-[:HAS_ANSWER]->(a_enabled:Answer) "
            "RETURN q_enabled, COLLECT(a_enabled) AS answers"
        )
        query: Neo4jQuery = Neo4jQuery(
            query_string,
            {
                "question_code": question_id.code,
                "answer_codes": [a.code for a in answer_ids],
            },
        )
        r: List[dict] = self.driver.query(query)
        if len(r) == 0:
            return None
        question: GraphQuestion = self._convert_node_in_question(
            r[0]["q_enabled"], r[0]["answers"]
        )
        return question

    def _check_question_exists(self, question_id: EntityId) -> bool:
        q: GraphQuestion = self.get_question_by_id(question_id)
        return q is not None

    def _check_answer_exists(self, answer_id: EntityId) -> bool:
        query_string = "MATCH (a:Answer {code: $answer_code}) RETURN a"
        query: Neo4jQuery = Neo4jQuery(query_string, {"answer_code": answer_id.code})
        r: List[dict] = self.driver.query(query)
        return len(r) > 0

    def _get_enabled_by(self, graph_question_id: EntityId) -> List[dict]:
        query_string = (
            "MATCH (q:GraphQuestion {code: $question_code}) "
            "OPTIONAL MATCH (q)-[:ENABLED_BY]->(a:Answer)<-[:HAS_ANSWER]-(q2:GraphQuestion) "
            "RETURN COLLECT(a.code) AS answer_code, COLLECT(q2.code) AS question_code"
        )
        query: Neo4jQuery = Neo4jQuery(
            query_string, {"question_code": graph_question_id.code}
        )
        r: List[dict] = self.driver.query(query)
        return [
            {"code": a, "question_code": q}
            for a, q in zip(r[0]["answer_code"], r[0]["question_code"])
        ]

    def _convert_question_in_node(self, question: GraphQuestion) -> dict:
        q: dict = serialize(question)
        del q["id"]
        q["code"] = question.id.code
        q["created_at"] = question.created_at.isoformat()
        del q["answers"]
        del q["enabled_by"]
        return q

    def _convert_node_in_question(self, q: dict, answers: List) -> GraphQuestion:
        question: dict = q
        question["id"] = {"code": question["code"]}
        question["description"] = (
            question["description"] if "description" in question else None
        )
        question["created_at"] = question["created_at"]
        question["answers"] = [
            {
                "id": {"code": a["code"], "question_code": question["id"]["code"]},
                "text": a["text"],
                "description": a["description"] if "description" in a else None,
            }
            for a in answers
        ]
        enabled_by: List[dict] = self._get_enabled_by(
            GraphQuestionFactory.id_of(question["id"]["code"])
        )
        question["enabled_by"] = enabled_by
        if "action_needed" in question:
            question["action_needed"] = question["action_needed"]
        else:
            question["action_needed"] = None
        return deserialize(question, GraphQuestion)

    def _convert_answer_in_node(self, answer: Answer) -> dict:
        a: dict = serialize(answer)
        a["code"] = answer.id.code
        del a["id"]
        return a

    def delete_all_questions(self) -> None:
        self.driver.transaction(
            [
                Neo4jQuery("MATCH (n:GraphQuestion) DETACH DELETE n", {}),
                Neo4jQuery("MATCH (n:Answer) DETACH DELETE n", {}),
            ]
        )

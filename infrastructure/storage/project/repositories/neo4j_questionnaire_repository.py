from typing import List, Optional

from domain.common.core import QuestionId
from domain.project.core import ProjectQuestion, Project, ProjectId, ProjectAnswer
from domain.project.repositories import ProjectRepository
from domain.project.repositories.questionnaire_repository import QuestionnaireRepository
from infrastructure.storage.project.repositories.neo4j_project_repository import (
    Neo4jProjectRepository,
)
from presentation.presentation import serialize, deserialize
from utils.env import DB_HOST, DB_USER, DB_PASSWORD
from utils.errors import NotFoundError
from utils.neo4j_driver import Neo4jDriver, Credentials, Neo4jQuery
from ws.utils.logger import logger


class Neo4jQuestionnaireRepository(QuestionnaireRepository):

    def __init__(self):
        self.driver: Neo4jDriver = Neo4jDriver(
            DB_HOST, Credentials(DB_USER, DB_PASSWORD)
        )
        self.project_repository: ProjectRepository = Neo4jProjectRepository()

    def get_nth_question(
        self, project_id: ProjectId, index: int
    ) -> Optional[ProjectQuestion]:
        if index <= 0:
            raise ValueError("Index must be greater than 0")
        elif index == 1:
            query_string: str = (
                "MATCH (p:Project {id: $project_code})-[:QUESTIONNAIRE]->(q:ProjectQuestion) "
                "OPTIONAL MATCH (q)-[:HAS_AVAILABLE]->(available:Answer) "
                "OPTIONAL MATCH (q)-[:HAS_SELECTED]->(selected:Answer) "
                "RETURN q, COLLECT(available) AS available_answers, COLLECT(selected) AS selected_answers"
            )
            query: Neo4jQuery = Neo4jQuery(
                query_string, {"project_code": project_id.code}
            )
            res: List[dict] = self.driver.query(query)
            if len(res) == 0:
                return None
            question: ProjectQuestion = self._convert_node_in_project_question(
                res[0]["q"],
                res[0]["available_answers"],
                res[0]["selected_answers"],
                None,
            )
            return question
        else:
            up_to_index: int = index - 1
            query_string: str = (
                "MATCH (p:Project {id: $project_code})-[:QUESTIONNAIRE]->(initial:ProjectQuestion) "
                "MATCH path = (initial)-[:NEXT*1..]->(:ProjectQuestion) "
                "WITH nodes(path) AS questions "
                "WITH questions[$index - 1] AS prev_q, questions[$index] AS q "
                "OPTIONAL MATCH (q)-[:HAS_AVAILABLE]->(available:Answer) "
                "OPTIONAL MATCH (q)-[:HAS_SELECTED]->(selected:Answer) "
                "RETURN q, COLLECT(available) AS available_answers, COLLECT(selected) AS selected_answers, prev_q"
            )
            query: Neo4jQuery = Neo4jQuery(
                query_string, {"project_code": project_id.code, "index": up_to_index}
            )
            res: List[dict] = self.driver.query(query)
            print(res[0]["q"])
            if len(res) == 0:
                return None
            question: ProjectQuestion = self._convert_node_in_project_question(
                res[0]["q"],
                res[0]["available_answers"],
                res[0]["selected_answers"],
                res[0]["prev_q"],
            )
            return question

    def get_last_question(self, project_id: ProjectId) -> Optional[ProjectQuestion]:
        query_string: str = (
            "MATCH (p:Project {id: $project_code})-[:QUESTIONNAIRE]->(initial:ProjectQuestion) "
            "MATCH path = (initial)-[:NEXT*0..]->(:ProjectQuestion) "
            "WITH nodes(path) AS questions "
            "RETURN questions[-1] AS q"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_code": project_id.code})
        res: List[dict] = self.driver.query(query)
        logger.info(f"RES {res}")
        if len(res) == 0:
            return None
        question: ProjectQuestion = self.get_project_question_by_id(
            QuestionId(code=res[0]["q"]["id"])
        )
        return question

    def get_project_question_by_id(
        self, question_id: QuestionId
    ) -> Optional[ProjectQuestion]:
        query_string: str = (
            "MATCH (q:ProjectQuestion {id: $question_id})-[:HAS_AVAILABLE]->(available:Answer) "
            "OPTIONAL MATCH (q)-[:HAS_SELECTED]->(selected:Answer) "
            "OPTIONAL MATCH (prev_q: ProjectQuestion)-[:NEXT]->(q)"
            "RETURN q, COLLECT(available) AS available_answers, COLLECT(selected) AS selected_answers, prev_q"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {"question_id": question_id.code})
        res: List[dict] = self.driver.query(query)
        if len(res) == 0:
            return None
        question: ProjectQuestion = self._convert_node_in_project_question(
            res[0]["q"],
            res[0]["available_answers"],
            res[0]["selected_answers"],
            res[0]["prev_q"],
        )
        return question

    def insert_project_question(self, question: ProjectQuestion) -> QuestionId:
        project_code: str = question.id.code.split("-")[0]
        project: Optional[Project] = self.project_repository.get_project_by_id(
            ProjectId(code=project_code)
        )
        if project is None:
            raise ValueError(f"Project with id {project_code} does not exist")
        queries: List[Neo4jQuery] = []
        q: dict = self._convert_project_question_in_node(question)
        query_string: str = (
            "MATCH (p:Project {id: $project_code}) "
            "CREATE (q:ProjectQuestion $question) "
        )
        query: Neo4jQuery = Neo4jQuery(
            query_string, {"project_code": project_code, "question": q}
        )
        queries.append(query)
        for answer in question.answers:
            a: dict = self._convert_answer_in_node(answer)
            queries.append(Neo4jQuery("CREATE (:Answer $answer)", {"answer": a}))
            relation_name: str = "HAS_SELECTED" if answer.selected else "HAS_AVAILABLE"
            queries.append(
                Neo4jQuery(
                    "MATCH (q:ProjectQuestion {id: $question_id}) "
                    "MATCH (a:Answer {id: $answer_id}) "
                    f"CREATE (q)-[:{relation_name}]->(a)",
                    {"question_id": question.id.code, "answer_id": answer.id.code},
                )
            )
        if question.previous_question_id is None:
            query_string: str = (
                "MATCH (p:Project {id: $project_code}) "
                "MATCH (q:ProjectQuestion {id: $question_id}) "
                "CREATE (p)-[:QUESTIONNAIRE]->(q)"
            )
            query: Neo4jQuery = Neo4jQuery(
                query_string,
                {"project_code": project_code, "question_id": question.id.code},
            )
            queries.append(query)
        else:
            previous_question: Optional[ProjectQuestion] = (
                self.get_project_question_by_id(question.previous_question_id)
            )
            if previous_question is None:
                raise ValueError(
                    f"Previous question with id {question.previous_question_id} does not exist"
                )
            query_string: str = (
                "MATCH (q:ProjectQuestion {id: $question_id}) "
                "MATCH (prev_q: ProjectQuestion {id: $prev_question_id}) "
                "CREATE (prev_q)-[:NEXT]->(q)"
            )
            query: Neo4jQuery = Neo4jQuery(
                query_string,
                {
                    "question_id": question.id.code,
                    "prev_question_id": question.previous_question_id.code,
                },
            )
            queries.append(query)

        self.driver.transaction(queries)
        return question.id

    def update_project_question(
        self, question_id: QuestionId, question: ProjectQuestion
    ) -> None:
        if not self._check_project_question_exists(question_id):
            raise NotFoundError(f"Question with id {question_id} does not exist")
        self.delete_project_question(question_id)
        self.insert_project_question(question)

    def delete_project_question(self, question_id: QuestionId) -> None:
        if not self._check_project_question_exists(question_id):
            raise NotFoundError(f"Question with id {question_id} does not exist")
        self.driver.query(
            Neo4jQuery(
                "MATCH (q:ProjectQuestion {id: $question_id})"
                "OPTIONAL MATCH (q)-[]->(a:Answer)"
                "OPTIONAL MATCH (prev_q: ProjectQuestion)-[:NEXT]->(q)"
                "OPTIONAL MATCH (p: Project)-[:QUESTIONNAIRE]->(q)"
                "DETACH DELETE q, a",
                {"question_id": question_id.code},
            )
        )

    def get_questionnaire(self, project_id: ProjectId) -> List[ProjectQuestion]:
        query_string: str = (
            "MATCH (p:Project {id: $project_code})-[:QUESTIONNAIRE]->(initial:ProjectQuestion) "
            "MATCH path = (initial)-[:NEXT*1..]->(:ProjectQuestion) "
            "WITH nodes(path) AS questions "
            "RETURN questions"
        )
        query: Neo4jQuery = Neo4jQuery(query_string, {"project_code": project_id.code})
        res: List[dict] = self.driver.query(query)
        questions: List[ProjectQuestion] = []
        for q in res[len(res) - 1]["questions"]:
            question: ProjectQuestion = self.get_project_question_by_id(
                QuestionId(code=q["id"])
            )
            questions.append(question)
        return questions

    def _check_project_question_exists(self, question_id: QuestionId) -> bool:
        q: ProjectQuestion = self.get_project_question_by_id(question_id)
        return q is not None

    def _convert_project_question_in_node(self, question: ProjectQuestion) -> dict:
        q: dict = serialize(question)
        q["id"] = question.id.code
        q["created_at"] = question.created_at.isoformat()
        q["selection_strategy"] = question.selection_strategy.__class__.__name__
        del q["answers"]
        del q["previous_question_id"]
        return q

    def _convert_answer_in_node(self, answer: ProjectAnswer) -> dict:
        a: dict = serialize(answer)
        a["id"] = answer.id.code
        del a["selected"]
        return a

    def _convert_node_in_answer(self, a: dict, selected: bool) -> ProjectAnswer:
        a["id"] = {"code": a["id"]}
        a["selected"] = selected
        return deserialize(a, ProjectAnswer)

    def _convert_node_in_project_question(
        self,
        q: dict,
        available_answers: List,
        selected_answers: List,
        previous_question: Optional[dict],
    ) -> ProjectQuestion:
        question: dict = q
        question["id"] = {"code": q["id"]}
        question["selection_strategy"] = {"type": q["selection_strategy"]}
        question["answers"] = [
            {
                "id": {"code": a["id"]},
                "text": a["text"],
                "selected": a in selected_answers,
            }
            for a in available_answers + selected_answers
        ]
        if previous_question:
            question["previous_question_id"] = (
                {"code": previous_question["id"]} if previous_question else None
            )
        else:
            question["previous_question_id"] = None
        return deserialize(question, ProjectQuestion)


if __name__ == "__main__":
    questionnaire_repository: QuestionnaireRepository = Neo4jQuestionnaireRepository()
    # project_question: ProjectQuestion = ProjectQuestionFactory.create_project_question(
    #     QuestionId(code="p1-Q-1"),
    #     text="What is your favorite color?",
    #     question_type=QuestionType.SINGLE_CHOICE,
    #     answers=frozenset(
    #         {
    #             ProjectAnswerFactory.create_project_answer(
    #                 AnswerId(code="p1-Q-1-A-1"), "Red"
    #             ),
    #             ProjectAnswerFactory.create_project_answer(
    #                 AnswerId(code="p1-Q-1-A-2"), "Green"
    #             ),
    #             ProjectAnswerFactory.create_project_answer(
    #                 AnswerId(code="p1-Q-1-A-3"), "Blue"
    #             ),
    #         }
    #     ),
    # )
    # updated_question: ProjectQuestion = project_question.select_answer(
    #     ProjectAnswerFactory.create_project_answer(
    #         AnswerId(code="p1-Q-1-A-1"), "Red"
    #     ).id
    # )
    # project_question2: ProjectQuestion = ProjectQuestionFactory.create_project_question(
    #     QuestionId(code="p1-Q-2"),
    #     text="What is your favorite animal?",
    #     question_type=QuestionType.SINGLE_CHOICE,
    #     answers=frozenset(
    #         {
    #             ProjectAnswerFactory.create_project_answer(
    #                 AnswerId(code="p1-Q-2-A-1"), "Dog"
    #             ),
    #             ProjectAnswerFactory.create_project_answer(
    #                 AnswerId(code="p1-Q-2-A-2"), "Cat"
    #             ),
    #             ProjectAnswerFactory.create_project_answer(
    #                 AnswerId(code="p1-Q-2-A-3"), "Bird"
    #             ),
    #         }
    #     ),
    #     previous_question_id=QuestionId(code="p1-Q-1"),
    # )
    # updated_question2: ProjectQuestion = project_question2.select_answer(
    #     ProjectAnswerFactory.create_project_answer(
    #         AnswerId(code="p1-Q-2-A-1"), "Dog"
    #     ).id
    # )
    #
    # questionnaire_repository.insert_project_question(project_question)
    # questionnaire_repository.update_project_question(
    #     project_question.id, updated_question
    # )
    # questionnaire_repository.insert_project_question(project_question2)
    # questionnaire_repository.update_project_question(
    #     project_question2.id, updated_question2
    # )
    # print(updated_question.selection_strategy.__class__.__name__)
    # print(questionnaire_repository.get_project_question_by_id(project_question.id))
    # print(questionnaire_repository.get_project_question_by_id(project_question2.id))
    # print(questionnaire_repository.get_nth_question(ProjectId(code="p1"), 1))
    print(questionnaire_repository.get_questionnaire(ProjectId(code="p1")))

    # questionnaire_repository.delete_project_question(project_question.id)
    # questionnaire_repository.delete_project_question(project_question2.id)

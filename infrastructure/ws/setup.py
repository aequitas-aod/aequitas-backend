from application.events import EventsService
from application.graph import GraphQuestionService
from application.logics.consumers import setup_consumers
from application.project.project_service import ProjectService
from application.project.questionnaire_service import QuestionnaireService
from domain.graph.repositories import GraphQuestionRepository
from domain.project.repositories import ProjectRepository
from domain.project.repositories.questionnaire_repository import QuestionnaireRepository
from infrastructure.events.kafka_events_service import KafkaEventsService
from infrastructure.storage.graph.repositories import Neo4JGraphQuestionRepository
from infrastructure.storage.project.repositories.neo4j_project_repository import (
    Neo4jProjectRepository,
)
from infrastructure.storage.project.repositories.neo4j_questionnaire_repository import (
    Neo4jQuestionnaireRepository,
)
from infrastructure.ws.utils import logger
from utils.env import ENV

graph_question_repository: GraphQuestionRepository = Neo4JGraphQuestionRepository()
question_service: GraphQuestionService = GraphQuestionService(graph_question_repository)

questionnaire_repository: QuestionnaireRepository = Neo4jQuestionnaireRepository()
questionnaire_service: QuestionnaireService = QuestionnaireService(
    questionnaire_repository,
    question_service,
)

project_repository: ProjectRepository = Neo4jProjectRepository()
project_service: ProjectService = ProjectService(project_repository)
events_service: EventsService = KafkaEventsService()

if ENV != "test":
    setup_consumers(events_service, project_service)

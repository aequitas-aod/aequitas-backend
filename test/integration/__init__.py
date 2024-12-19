import unittest
from python_on_whales import DockerClient
from utils.logs import logger
from pathlib import Path
import test
import tempfile
from resources.db import PATH_INIT_CYPHER as RESOURCE_INIT_CYPHER
import atexit
import shutil


DIR_PROJECT = Path(test.__file__).parent.parent
DIR_INTEGRATION_TESTS = Path(
    tempfile.mkdtemp(prefix="aequitas-backend-integration-tests")
)
logger.info(f"Integration tests directory: {DIR_INTEGRATION_TESTS}")

PATH_DOCKER_COMPOSE_SPEC = DIR_INTEGRATION_TESTS / "docker-compose.yml"
CODE_NEO4J_INIT = ""  # do not initialize the database

PATH_DOCKER_COMPOSE_SPEC.write_text(
    test.docker_compose_spec(NEO4J_INITIALIZATION_CODE=CODE_NEO4J_INIT)
)

PATH_INIT_CYPHER = DIR_INTEGRATION_TESTS / "init.cypher"
PATH_INIT_CYPHER.write_text(RESOURCE_INIT_CYPHER.read_text())

PATH_NEO4J_HEALTH_CHECK = DIR_INTEGRATION_TESTS / "neo4j-healthcheck.sh"
PATH_NEO4J_HEALTH_CHECK.write_text((DIR_PROJECT / "neo4j-healthcheck.sh").read_text())


docker_client = DockerClient(compose_project_directory=DIR_INTEGRATION_TESTS)


def _cleanup():
    try:
        logger.info("Cleaning up docker compose")
        docker_client.compose.down(volumes=True)
    finally:
        logger.info(
            "Cleaning up integration tests directory: %s", DIR_INTEGRATION_TESTS
        )
        shutil.rmtree(DIR_INTEGRATION_TESTS)


atexit.register(_cleanup)


class DockerComposeBasedTestCase(unittest.TestCase):
    services = {"db"}

    @classmethod
    def startDocker(cls):
        cls.docker = docker_client
        cls.docker.compose.up(services=list(cls.services), detach=True, wait=True)

    @classmethod
    def setUpClass(cls):
        cls.startDocker()

    @classmethod
    def tearDownClass(cls):
        cls.docker.compose.down(volumes=True)

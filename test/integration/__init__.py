import atexit
import shutil
import tempfile
import unittest
from pathlib import Path

from python_on_whales import DockerClient

import test.resources
from resources.db import PATH_INIT_CYPHER as RESOURCE_INIT_CYPHER
from utils.logs import logger

DIR_PROJECT = Path(test.__file__).parent.parent
DIR_INTEGRATION_TESTS = Path(
    tempfile.mkdtemp(prefix="aequitas-backend-integration-tests")
)
logger.info(f"Integration tests directory: {DIR_INTEGRATION_TESTS}")

PATH_DOCKER_COMPOSE_SPEC = DIR_INTEGRATION_TESTS / "docker-compose.yml"
CODE_NEO4J_INIT = ""  # do not initialize the database

PATH_DOCKER_COMPOSE_SPEC.write_text(
    test.resources.docker_compose_spec(NEO4J_INITIALIZATION_CODE=CODE_NEO4J_INIT)
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
    up_services_before = True
    down_services_after = False

    @classmethod
    def startDockerServices(cls):
        cls.docker.compose.up(
            services=list(cls.services), detach=True, wait=True, build=True
        )

    @classmethod
    def stopDockerServices(cls):
        cls.docker.compose.down(services=list(cls.services), volumes=True)

    @classmethod
    def setUpClass(cls):
        cls.docker = docker_client
        if cls.up_services_before:
            cls.startDockerServices()

    @classmethod
    def tearDownClass(cls):
        if cls.down_services_after:
            cls.stopDockerServices()

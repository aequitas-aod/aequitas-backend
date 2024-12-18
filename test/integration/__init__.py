import unittest
from python_on_whales import DockerClient


class DockerComposeBasedTestCase(unittest.TestCase):
    services = { 'db' }

    @classmethod
    def startDocker(cls):
        cls.docker = DockerClient()
        cls.docker.compose.down(volumes=True)
        cls.docker.compose.up(services=list(cls.services), detach=True, wait=True)

    @classmethod
    def setUpClass(cls):
        cls.startDocker()

    @classmethod
    def tearDownClass(cls):
        cls.docker.compose.down(volumes=True)

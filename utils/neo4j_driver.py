from typing import List, Optional

import backoff
from neo4j import GraphDatabase, Driver, Result
from neo4j.exceptions import ServiceUnavailable, SessionExpired

import utils.env
from utils.logs import set_other_loggers_level

# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()


class Credentials:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password


class Neo4jQuery:
    def __init__(self, query: str, params: dict):
        self.query: str = query
        self.params: dict = params
        self.result: Optional[Result] = None


class Neo4jDriver:

    def __init__(self, host: str, credentials: Credentials):
        self.retries = 10
        self.delay = 1
        self.driver: Driver = GraphDatabase.driver(
            f"neo4j://{host}",
            auth=(credentials.user, credentials.password),
        )

    @backoff.on_exception(
        backoff.expo, (ServiceUnavailable, SessionExpired), max_tries=10
    )
    def query(self, query: Neo4jQuery) -> List[dict]:
        """
        Execute a query and return the results as a list of dictionaries.
        It also stores the Result in the query object.
        :param Neo4jQuery query: Query to be executed
        :return: Results as a list of dictionaries
        """
        with self.driver.session() as session:
            result: Result = session.run(query.query, **query.params)
            query.result = result
            return result.data()

    @backoff.on_exception(
        backoff.expo, (ServiceUnavailable, SessionExpired), max_tries=10
    )
    def transaction(self, queries: List[Neo4jQuery]) -> None:
        """
        Execute a list of queries in a single transaction.
        Each query can use the results of the previous queries as parameters.
        For example:
        queries = [
            Neo4jQuery("MATCH (n:Node {code: $node_code}) RETURN n.name AS node_name", {"node_code": "123"}),
            Neo4jQuery("MATCH (n:Node {name: $node_name}) RETURN n", {}),
        ]
        :param List[Neo4jQuery] queries: List of queries to be executed
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                results: dict[str, any] = {}
                for query in queries:
                    result: Result = tx.run(query.query, **(query.params | results))
                    for dic in result.data():
                        results = results | dic

                tx.commit()

    def close(self):
        self.driver.close()

import json
from typing import List

from kafka3 import KafkaProducer

from infrastructure.events import KafkaBroker, get_brokers_from_env
from infrastructure.ws.utils import logger


class Producer:

    def __init__(self):
        brokers: List[KafkaBroker] = get_brokers_from_env()
        logger.info(f"Connecting to Kafka brokers: {brokers}")
        self._producer = KafkaProducer(
            bootstrap_servers=list(
                map(lambda broker: f"{broker.host}:{broker.port}", brokers)
            ),
        )

    def produce(self, topic: str, message: dict):
        self._producer.send(topic, json.dumps(message).encode("utf-8"))

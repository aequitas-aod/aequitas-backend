import json
from typing import List

from kafka3 import KafkaProducer

from infrastructure.events import KafkaBroker, get_brokers_from_env
from infrastructure.ws.utils import logger


class Producer:

    def __init__(self):
        self._brokers: List[KafkaBroker] = get_brokers_from_env()
        logger.info(f"Connecting to Kafka brokers: {self._brokers}")
        self._producer: KafkaProducer = KafkaProducer(
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            bootstrap_servers=list(
                map(lambda broker: f"{broker.host}:{broker.port}", self._brokers)
            ),
        )

    def produce(self, topic: str, message: dict | str):
        print(f"Producing message to topic '{topic}':\n{message}")
        self._producer.send(topic, message)
        self._producer.flush()
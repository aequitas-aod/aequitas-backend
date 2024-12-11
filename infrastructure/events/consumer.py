import json
from multiprocessing import Process
from typing import List, Dict

from kafka3 import KafkaConsumer
from typing_extensions import Callable

from infrastructure.events import KafkaBroker, get_brokers_from_env
from infrastructure.ws.utils import logger


class Consumer:

    def __init__(self, topics: List[str], handler: Callable[[Dict], None]) -> None:
        self.is_consuming: bool = False
        self._brokers: List[KafkaBroker] = get_brokers_from_env()
        self._handler: Callable[[Dict], None] = handler
        self._topics = topics
        logger.info(f"Connected to Kafka brokers: {self._brokers}")

    def _consume_messages(self) -> None:
        consumer = KafkaConsumer(
            *self._topics,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            bootstrap_servers=[f"{broker.host}:{broker.port}" for broker in self._brokers],
            auto_offset_reset="latest",  # Start consuming from the end of the topic.
        )

        for message in consumer:
            self._handler(message)

    def start_consuming(self) -> None:
        if self.is_consuming:
            raise ValueError("Consumer is already consuming")
        self.is_consuming = True
        consumer_process = Process(target=self._consume_messages)
        consumer_process.start()

import json
import threading
from typing import List

from kafka3 import KafkaConsumer
from typing_extensions import Callable

from infrastructure.events import KafkaBroker, get_brokers_from_env
from infrastructure.ws.utils import logger


class Consumer:

    def __init__(self, topics: List[str], handler: Callable[[dict], None]) -> None:
        self.is_consuming: bool = False
        self._brokers: List[KafkaBroker] = get_brokers_from_env()
        self._handler: Callable[[dict], None] = handler
        self._consumer: KafkaConsumer = KafkaConsumer(
            *topics,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            bootstrap_servers=list(
                map(lambda broker: f"{broker.host}:{broker.port}", self._brokers)
            ),
            auto_offset_reset="latest",  # Start consuming from the end of the topic.
        )
        logger.info(f"Connected to Kafka brokers: {self._brokers}")

    def start_consuming(self) -> None:
        if self.is_consuming:
            raise ValueError("Consumer is already consuming")

        def consume():
            for message in self._consumer:
                self._handler(message)

        threading.Thread(target=consume).start()

        self.is_consuming = True

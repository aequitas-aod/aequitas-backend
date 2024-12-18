import json
from threading import Thread
from typing import List

import backoff
from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from kafka.errors import NoBrokersAvailable, UnrecognizedBrokerVersion
from typing_extensions import Callable

from infrastructure.events import KafkaBroker, get_brokers_from_env
from utils.logs import logger


class Consumer:

    def __init__(
        self, topics: List[str], handler: Callable[[ConsumerRecord], None]
    ) -> None:
        self.is_consuming: bool = False
        self._brokers: List[KafkaBroker] = get_brokers_from_env()
        self._handler: Callable[[ConsumerRecord], None] = handler
        self._topics = topics
        logger.info(f"Connected to Kafka brokers: {self._brokers}")

    @backoff.on_exception(
        backoff.expo, (NoBrokersAvailable, UnrecognizedBrokerVersion), max_tries=10
    )
    def _consume_messages(self) -> None:
        consumer = KafkaConsumer(
            *self._topics,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            bootstrap_servers=[
                f"{broker.host}:{broker.port}" for broker in self._brokers
            ],
            auto_offset_reset="latest",  # Start consuming from the end of the topic.
        )

        for message in consumer:
            self._handler(message)

    def start_consuming(self) -> None:
        if self.is_consuming:
            raise ValueError("Consumer is already consuming")
        self.is_consuming = True
        consumer_thread = Thread(target=self._consume_messages, daemon=True)
        consumer_thread.start()

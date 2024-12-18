from typing import List, Callable

from kafka.consumer.fetcher import ConsumerRecord

from application.events import EventsService
from infrastructure.events import Producer, Consumer
from utils.logs import set_other_loggers_level
import utils.env


# if testing, lowers the visibility of non-aequitas logs
if utils.env.is_testing():
    set_other_loggers_level()


class KafkaEventsService(EventsService):

    def __init__(self):
        self._producer = None

    def publish_message(self, topic: str, message: str) -> None:
        if self._producer is None:
            self._producer = Producer()
        self._producer.produce(topic, message)

    def start_consuming(
        self, topics: List[str], handler: Callable[[ConsumerRecord], None]
    ) -> None:
        Consumer(topics, handler).start_consuming()

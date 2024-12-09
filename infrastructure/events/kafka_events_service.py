from typing import List, Callable

from application.events import EventsService
from infrastructure.events import Producer, Consumer


class KafkaEventsService(EventsService):

    def __init__(self):
        self._producer = Producer()

    def publish_message(self, topic: str, message: str) -> None:
        self._producer.produce(topic, message)


    def start_consuming(self, topics: List[str], handler: Callable[[dict], None]) -> None:
        Consumer(topics, handler).start_consuming()


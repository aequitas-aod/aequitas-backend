from abc import ABC
from typing import List, Callable, Dict


class EventsService(ABC):

    def publish_message(self, topic: str, message: str | Dict) -> None:
        """
        Publishes a message to the event infrastructure
        :param topic: the topic to publish the message to
        :param message: the message to publish
        """

    def start_consuming(
        self, topics: List[str], handler: Callable[[Dict], None]
    ) -> None:
        """
        Starts consuming messages from the event infrastructure
        :param topics: the topics to consume messages from
        :param handler: the function to call when a message is consumed
        """

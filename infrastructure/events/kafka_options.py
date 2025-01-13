import os
import re
from typing import List


class KafkaBroker:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    def __repr__(self):
        return f"KafkaBroker(host='{self.host}', port='{self.port}')"


PATTERN_KAFKA_HOST = re.compile(r"^KAFKA(_EXTERNAL)?_HOST")
PATTERN_KAFKA_PORT = re.compile(r"^KAFKA(_EXTERNAL)?_PORT")


def get_brokers_from_env() -> List[KafkaBroker]:
    broker_hosts = []
    broker_ports = []

    for variable, value in os.environ.items():
        if PATTERN_KAFKA_HOST.match(variable):
            broker_hosts.append(value)
        elif PATTERN_KAFKA_PORT.match(variable):
            broker_ports.append(value)

    if len(broker_hosts) != len(broker_ports):
        raise ValueError("Invalid configuration for Kafka brokers")

    return [
        KafkaBroker(host, broker_ports[index])
        for index, host in enumerate(broker_hosts)
    ]

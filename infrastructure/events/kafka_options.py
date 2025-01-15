import os
from typing import List

from utils.env import is_testing


class KafkaBroker:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    def __repr__(self):
        return f"KafkaBroker(host='{self.host}', port='{self.port}')"


def get_brokers_from_env() -> List[KafkaBroker]:
    broker_hosts = []
    broker_ports = []

    host_prefix = "KAFKA_EXTERNAL_HOST" if is_testing() else "KAFKA_HOST"
    port_prefix = "KAFKA_EXTERNAL_PORT" if is_testing() else "KAFKA_PORT"

    for variable, value in os.environ.items():
        if variable.startswith(host_prefix):
            broker_hosts.append(value)
        elif variable.startswith(port_prefix):
            broker_ports.append(value)

    if len(broker_hosts) != len(broker_ports):
        raise ValueError("Invalid configuration for Kafka brokers")

    return [
        KafkaBroker(host, broker_ports[index])
        for index, host in enumerate(broker_hosts)
    ]

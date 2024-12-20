import base64
from typing import Union

from utils.logs import logger


def encode(value: str) -> str:
    logger.info("Encoding value")
    logger.info(type(value))
    encoded_bytes = base64.b64encode(value.encode("utf-8"))
    logger.info("ENCODED")
    return encoded_bytes.decode("utf-8")


def decode(value: str) -> str:
    decoded_bytes = base64.b64decode(value.encode("utf-8"))
    return decoded_bytes.decode("utf-8")

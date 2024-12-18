import base64
from typing import Union


def encode(value: Union[str, bytes]) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    encoded_bytes = base64.b64encode(value)
    return encoded_bytes.decode("utf-8")


def decode(value: str) -> str:
    decoded_bytes = base64.b64decode(value.encode("utf-8"))
    return decoded_bytes.decode("utf-8")

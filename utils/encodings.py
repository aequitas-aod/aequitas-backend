import base64


def encode(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    encoded_bytes = base64.b64encode(value)
    return encoded_bytes.decode("utf-8")


def decode(value: str) -> bytes:
    return base64.b64decode(value.encode("utf-8"))

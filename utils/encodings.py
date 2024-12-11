import base64


def encode(value: str) -> str:
    encoded_bytes = base64.b64encode(value.encode("utf-8"))
    return encoded_bytes.decode("utf-8")


def decode(value: str) -> str:
    decoded_bytes = base64.b64decode(value.encode("utf-8"))
    return decoded_bytes.decode("utf-8")

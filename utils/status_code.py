from enum import Enum


class StatusCode(int, Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    UNSUPPORTED_MEDIA_TYPE = 415
    INTERNAL_SERVER_ERROR = 500

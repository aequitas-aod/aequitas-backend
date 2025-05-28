from dataclasses import dataclass, field

from utils.status_code import StatusCode


@dataclass
class NotFoundError(Exception):
    message: str
    status_code: int = field(init=False, default=StatusCode.NOT_FOUND)

    def __str__(self):
        return repr(self.message)


@dataclass
class ConflictError(Exception):
    message: str
    status_code: int = field(init=False, default=StatusCode.CONFLICT)

    def __str__(self):
        return repr(self.message)


@dataclass
class BadRequestError(Exception):
    message: str
    status_code: int = field(init=False, default=StatusCode.BAD_REQUEST)

    def __str__(self):
        return repr(self.message)


@dataclass
class MissingFirstQuestion(Exception):
    def __init__(self):
        super().__init__()

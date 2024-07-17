from utils.status_code import StatusCode


class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.status_code = StatusCode.NOT_FOUND

    def __str__(self):
        return repr(self.message)


class ConflictError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.status_code = StatusCode.CONFLICT

    def __str__(self):
        return repr(self.message)


class BadRequestError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.status_code = StatusCode.BAD_REQUEST

    def __str__(self):
        return repr(self.message)

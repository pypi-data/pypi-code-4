class BaseException(Exception):
    pass


class FieldTypeError(BaseException):
    pass


class NotPrimaryError(BaseException):
    pass


class InvalidArgumentError(BaseException):
    pass

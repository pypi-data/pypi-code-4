class ApplicationError(Exception):
    """
    Raised by application logic.l
    """
    pass


class ArgumentError(ApplicationError):
    """
    Raised on unexpected actions which should not occur during normal usage,
    e.g. an user sends crafted HTTP header or opens URL which link does not exist anywhere in the application.
    """
    pass


class ValidationError(ApplicationError):
    """
    Raised when data provided by user does not match the requirements,
    e.g. an user sends /root or parent directory as the argument of an action.
    """
    pass

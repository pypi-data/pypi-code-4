class UnipagException(Exception):
    """
    Parent for all Unipag exceptions.
    """

    def __init__(self, msg=None, http_code=None, http_body=None,
                 json_body=None):
        super(UnipagException, self).__init__(msg)
        self.http_code = http_code
        self.http_body = http_body
        self.json_body = json_body


class ConnectionError(UnipagException):
    """
    Unable to connect to Unipag API.
    """


class APIError(UnipagException):
    """
    There was a problem with Unipag API.
    """


class Unauthorized(UnipagException):
    """
    You did not provide a valid API key.
    """


class BadRequest(UnipagException):
    """
    Some of request parameters passed to Unipag were invalid.
    """


class Forbidden(UnipagException):
    """
    Access denied.
    """


class NotFound(UnipagException):
    """
    Requested object does not exist in Unipag.
    """


class MethodNotAllowed(UnipagException):
    """
    Requested method is not allowed for this object.
    """


class InternalError(UnipagException):
    """
    Internal Unipag error.
    """


class BadGateway(UnipagException):
    """
    Unexpected error occurred while communicating with target payment gateway.
    """


class ServiceUnavailable(UnipagException):
    """
    There was a problem while trying to fulfill your request.
    """

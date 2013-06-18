class ToothpickError(Exception):
    pass

class RecordInvalidError(ToothpickError): pass


# HTTP response errors
class ResponseError(ToothpickError):
    def __init__(self, response=None, *args, **kwargs):
        self.response = response
        super(ResponseError, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "%s: %s" % (
            self.__class__.__name__,
            repr(self.response)
        )

    def __str__(self):
        return repr(self)

class BadRequest(ResponseError):
    '''Raised for HTTP 400'''
    pass

class Unauthorized(ResponseError):
    '''Raised for HTTP 401'''
    pass

class Forbidden(ResponseError):
    '''Raised for HTTP 403'''
    pass

class NotFound(ResponseError):
    '''Raised for HTTP 404'''
    pass

class MethodNotAllowed(ResponseError):
    '''Raised for HTTP 405'''
    pass

class Conflict(ResponseError):
    '''Raised for HTTP 409'''
    pass

class Invalid(ResponseError):
    '''Raised for HTTP 422'''
    pass

class ClientError(ResponseError):
    '''Raised for other HTTP codes between 400 and 499'''
    pass

class ServerError(ResponseError):
    '''Raised for other HTTP codes between 500 and 599'''
    pass


class TooManyRecordsError(ToothpickError):
    pass


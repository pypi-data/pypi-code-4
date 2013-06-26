import json

class EligibleError(Exception):
    '''Base class for all API errors/exceptions'''
    def __init__(self, msg, http_status=None, http_body=None):
        self.msg = msg
        self.http_status = http_status
        self.http_body = http_body
        try:
            self.json_body = json.loads(http_body)
        except (ValueError, TypeError):
            self.json_body = None # No json could be decoded.

    def __repr__(self):
        return "{message}".format(message=('({}) '.format(self.http_status) if self.http_status else '') + self.msg)

    def __str__(self):
        return repr(self)


class APIError(EligibleError):
    '''General API error for when failures can't be attributed to something more specific'''
    pass


class APIConnectionError(EligibleError):
    '''Raised when the API cannot be reached'''
    pass


class AuthenticationError(EligibleError):
    '''Raised if no API key is set or if the API Key is bad'''
    pass


class InvalidRequestError(EligibleError):
    '''
    Raised if the client hasn't passsed in the right params
    meaning the request can't be processed properly.
    '''
    pass

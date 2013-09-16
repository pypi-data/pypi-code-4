from __future__ import absolute_import
from protorpc import messages as messages

class APIError(Exception):
    """ 
    http://www.jsonrpc.org/historical/json-rpc-over-http.html
    """
    class ErrorType(messages.Enum):
        PARSE_ERROR = 1 # 500
        INVALID_REQUEST = 2 # 400
        METHOD_NOT_FOUND = 3 # 404
        INVALID_PARAMS = 4 # 500
        INTERNAL_ERROR = 5 # 500
        SERVER_ERROR = 6 # 500
        
    ERROR_NO_METHOD = 1
    ERROR_INVALID_VERSION = 2
    ERROR_INVALID_BODY = 3
    ERROR_INVALID_REQUEST = 5
    ERROR_INVALID_RESPONSE = 6
    ERROR_UNKNOWN_EXCEPTION = 7
    
    class ErrorMessage(messages.Message):
        code = messages.IntegerField(1)
        message = messages.StringField(2)

    def __init__(self, code, message):
        self.message = self.ErrorMessage(code=code, message=message)
        
        
        
class ServiceError(APIError):
    class ErrorMessage(messages.Message):
        code = messages.IntegerField(1, default=APIError.ERROR_UNKNOWN_EXCEPTION)
        message = messages.StringField(2)

    def __init__(self, message='Server error!'):
        self.message = self.ErrorMessage(message=message)
    
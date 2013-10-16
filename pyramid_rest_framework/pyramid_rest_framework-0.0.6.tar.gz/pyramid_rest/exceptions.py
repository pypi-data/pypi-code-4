#-*- coding: utf-8 -*-
from pyramid_rest.logger import Logger
import traceback

class ExceptionInterface:
    """
        Общий интерфейс для HTTP ошибок.
    """
    code = 500
    name = "Internal Server Error"
    info = ""
    def __init__(self, **k):
        old_trace = traceback.format_exc()
        if len(old_trace) > 10:
            Logger().main.error("Raised internal exception. Original trace: %s", 
                                old_trace)
        
        for key, value in k.iteritems():
            if not hasattr(self, key):
                raise Exception("Incorrect key passed into exception  constructor")
            setattr(self, key, value)
            
    def serialize(self, request):
        request.request.response.status_code = self.code
        request.response_code = self.code
        
        out = {"code": self.code,
                "name": self.name,
                "info": self.info}
        
        request.response = out
        return out
    
    def pyramid_serialize(self, pyramid_request):
        pyramid_request.response.status_code = self.code
        pyramid_request.response.status_code = self.code
        
        out = {"code": self.code,
                "name": self.name,
                "info": self.info}
    
        return out
        
class UnknownError(ExceptionInterface):
    name = "UnknownError"

class MethodNotAllowed(ExceptionInterface):
    code = 405
    name = "MethodNowAllowed"

class Unauthorized(ExceptionInterface):
    code = 401
    name = "Unauthorized"

class BadRequest(ExceptionInterface):
    code = 400
    name = "BadRequest"
    
class ValidationError(BadRequest):
    name = "ValidationError"
    
class Forbidden(ExceptionInterface):
    code = 403
    name = "Forbidden"
    
#-*- coding: utf-8 -*-

class ExceptionInterface:
    """
        Общий интерфейс для HTTP ошибок.
    """
    code = 500
    name = "Internal Server Error"
    info = ""
    def __init__(self, **k):
        for key, value in k.iteritems():
            if not hasattr(self, key):
                raise Exception("Incorrect key passed into exception  constructor")
            setattr(self, key, value)
            
    def serialize(self, request):
        request.request.response.status_code = self.code
        return {"code": self.code,
                "name": self.name,
                "info": self.info}

class UnknownError(ExceptionInterface):
    name = "UnknownError"

class MethodNotAllowed(ExceptionInterface):
    code = 405
    name = "MethodNowAllowed"
    
class BadRequest(ExceptionInterface):
    code = 400
    name = "BadRequest"
    
class ValidationError(BadRequest):
    name = "ValidationError"
    
class Forbidden(ExceptionInterface):
    code = 403
    name = "Forbidden"
    
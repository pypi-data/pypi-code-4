#-*- coding: utf-8 -*-

class Response:
    def __init__(self, request, data, code):
        self.data = data
        self.code = code
        self.request = request
        
    def serialize(self):
        self.request.request.status_code = self.code
        return self.data
        
    
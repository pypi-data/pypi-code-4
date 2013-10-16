#-*- coding: utf-8 -*-
from pyramid_rest.exceptions import ExceptionInterface
from pyramid_rest.events import EventManager
from pyramid_rest.request import Request
from pyramid_rest.response import Response


class View:
    """
        Используется как обертка над функцией представления, которая регистрируется в 
        :func:`pyramid_rest.server.Server.add_route`
        
        Обертка выполняет следующие функции:
        
            * отлавливает ошибки
    """
    
    def __init__(self, app, view):
        self.app = app
        self.view = view
        
        self.app.logger.view.info("Registered view wrapper")
        
        
    def __call__(self, pyramid_request):
        try:
            request = Request(pyramid_request)
            EventManager().trigger("before-request", self, request)
            response = self.view(request)
            code = 200
        except ExceptionInterface as x:
            response = x.serialize(request)
            code = x.code
            
        responseClass = Response(request, response, code)
        EventManager().trigger("before-response", self, request, responseClass)
        
        return responseClass.serialize()
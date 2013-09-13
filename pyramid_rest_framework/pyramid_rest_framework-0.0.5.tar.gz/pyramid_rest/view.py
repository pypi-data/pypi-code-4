#-*- coding: utf-8 -*-
from pyramid_rest.exceptions import ExceptionInterface
from pyramid_rest.events import EventManager
from pyramid_rest.request import Request


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
        request = Request(pyramid_request)
        EventManager().trigger("before-request", self, request)
        try:
            response = self.view(request)
        except ExceptionInterface as x:
            response = x.serialize(request)
        EventManager().trigger("before-response", self, request, response)
        return response
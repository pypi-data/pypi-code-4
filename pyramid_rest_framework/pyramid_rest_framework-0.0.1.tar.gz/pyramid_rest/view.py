#-*- coding: utf-8 -*-
from pyramid_rest.exceptions import ExceptionInterface


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
            response = self.view(pyramid_request)
        except ExceptionInterface as x:
            return x.serialize(pyramid_request)
        
        return response
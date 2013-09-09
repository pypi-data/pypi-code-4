#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone
from pyramid_rest.view import View

class Server:
    def __init__(self, app):
        self.app = app
        self.app.logger.server.info("Server initilized")
        
    def add_route(self, name, url, view):
        """
            Добавляет обычный pyramid-route. По сути обертка над config.add_route
            
            :param name: Название роута. Все названия должны быть уникальными!
            :param url: URL
            :param view: функция-представление. Вызывается при обращении к роуту и принимает объект pyramid-request
        """
        self.app.config.add_route(name, url, view = View(self.app, view), renderer = "json")
        self.app.logger.server.info("Added route with name: %s; url: %s", name, url)
    
        
    
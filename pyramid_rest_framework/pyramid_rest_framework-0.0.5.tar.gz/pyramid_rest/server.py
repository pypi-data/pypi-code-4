#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone
from pyramid_rest.view import View
from pyramid_rest.events import EventManager

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
        EventManager().trigger("before-add-route", self, name, url, view)
        self.app.config.add_route(name, url, view = View(self.app, view), renderer = "json")
        self.app.logger.server.info("Added route with name: %s; url: %s", name, url)
        EventManager().trigger("after-add-route", self, name, url, view)
    
        
    
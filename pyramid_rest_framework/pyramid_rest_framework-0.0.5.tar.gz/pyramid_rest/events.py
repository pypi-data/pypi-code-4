#-*- coding: utf-8 -*-
"""
Класс для установки произвольных событий и обработчиков на них.
На каждое событие можно установить несколько обработчиков, при этом они будут выполняться последовательно, в том порядке,
в котором они были установленны.
"""
from pyramid_rest.helpers import singletone
from pyramid_rest.logger import Logger

@singletone
class EventManager:
    """
        Класс для работы с событиями.
        
        Везде далее initiator - инстанс класса,внутри которого вызвано событие.
        
        Framework-defined события:
        
            * **after-app-initialize(initiator)** - срабатывает после инициализации :class:`pyramid_rest.app.App`
            * **before-request(initiator, request)** - срабатывает перед вызовом представления.
                :param request: - текущий инстанс :class:`pyramid_rest.request.Request`
            * **before-response(initiator, request, response_object)** - срабатывает сразу после вызова представления, перед ответом сервера.
                :param request: - текущий инстанс :class:`pyramid_rest.request.Request`
                :param response_object: JSON объект ответа.
            * **before-add-route(initiator, name, url, view)** срабатывает перед созданием route
                :param name: - имя роута
                :param url: - url роута
                :param view: - функция - представление, обрабатывающее роут
                
            * **after-add-route(self, name, url, view)** - срабатывает сразу после создания route
                
    """
    LISTENERS = {}
    def __init__(self):
        pass
    
    def bind(self, event, handler_function):
        """
            Привязывает к событию функцию - обработчик. 
            
            .. note::
            
                У каждого события может быть несколько обработчиков, при этом они выполняются независимо, последовательно в том порядке, в котором были созданы.

        """
        if event in self.LISTENERS:
            self.LISTENERS[event].append(handler_function)
        else:
            self.LISTENERS[event] = [handler_function]
    
    def trigger(self, event, *a, **k):
        """
            Вызывает обработчик(и) события event с аргументами *a, **k
        """
        Logger().events.info("Triggered event %s", event)
        if event not in self.LISTENERS:
            Logger().events.warning("No handlers founded for event %s", event)
        for func in self.LISTENERS.get(event, []):
            func(*a, **k)
    
    def unbind(self, event):
        """
            Удаляет **все** обработчики события.
        """
        del self.LISTENERS[event]
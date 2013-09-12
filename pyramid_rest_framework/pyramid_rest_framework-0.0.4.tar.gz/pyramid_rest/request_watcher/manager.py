#-*- coding: utf-8 -*-
"""
Класс для обработки ошибок и отслеживания всех запросов к системе.
"""
from pyramid_rest.helpers import singletone, get_ip, get_or_none, send_message
from pyramid_rest.request_watcher.models import Request, Response
import transaction
from pprint import pformat
from sqlalchemy_admin.db_wrapper import NotOverloadedError
import traceback
import datetime
import logging
import json
from pyramid_rest.config import Config
from pyramid_rest.events import EventManager
from pyramid_rest.logger import Logger


class HandlerInterface:
    def __init__(self):
        pass
    
    def handle_response(self, request, code, body):
        raise NotOverloadedError
    
class db(HandlerInterface):
    def handle_response(self, request, code, body):
        wrapped_request = request
        request = getattr(request, "request", None) or request
        with transaction.manager:
            db_request_id = Request(host = request.headers["host"],
                    path = request["PATH_INFO"],
                    ip = get_ip(request),
                    user_id = get_or_none(wrapped_request, "userid"),
                    request = pformat(request.__dict__),
                    method = request.method.lower(),
                    query = pformat(dict(request.GET)),
                    data = pformat(dict(request.POST)),
                    headers = pformat(dict(request.headers)))._add()._flush().id
                    
            Response(request_id = db_request_id,
                     code = code, 
                     body = body)._add()
                     
class email(HandlerInterface):
    def __init__(self):
        self.config_parsed = False
        
        HandlerInterface.__init__(self)
    
    def _parse_config(self):
        if self.config_parsed == True:
            return
        
        try:
            self.recipients = json.loads(Config()["pyramid_rest.request_watcher.handlers.email.recipients"])
            self.sender = json.loads(Config()["pyramid_rest.request_watcher.handlers.email.sender"])
        except Exception as x:
            raise AttributeError("Not all params correctly defined. Full exception: %s"%x)
        self.config_parsed = True
        
    def handle_response(self, request, code, body):
        self._parse_config()
        request = request.request
        BODY = u"""
            Критическая ошибка на %(full_path)s.
            <br>
            <h3>Session info:</h3>
            <ul>
                <li><b>Datetime:</b> - %(dt)s</li>
                <li><b>Full path: </b> - %(full_path)s</li>
                <li><b>User IP:</b> - %(ip)s</li>
                <li><b>User email: </b> - %(email)s</li>
            </ul>
            <h3>Trace:</h3>
            <pre>%(trace)s</pre>
            <br>
            <h3>Request type:</h3>
            <br>%(full_path)s
            %(request_type)s
            <br>    
            <h3>Get data:</h3>
            <pre>%(get)s</pre>
            <br>
            <h3>Post data:</h3>
            <pre>%(post)s</pre>
            <br>
            <h3>Headers:</h3>
            <pre>%(headers)s</pre>
            <br>
            <h3>Request:</h3>
            <pre>
                %(request)s
            </pre>
            
            
                
            """%({"full_path": request["PATH_INFO"],
                  "ip": get_ip(request),
                  "dt": datetime.datetime.now(),
                  "email": get_or_none(request, "user", "email"),
                  "request": pformat(request.__dict__),
                  "request_type": request.method,
                  "get": pformat(dict(request.GET)),
                  "post": pformat(dict(request.POST)),
                  "headers": pformat(dict(request.headers)),
                  "trace": traceback.format_exc()})
        send_message(request, 
                     subject = u"Критическая ошибка на %s %s."%(request.headers["host"], 
                                                                request["PATH_INFO"]),
                     sender = self.sender,
                     recipients = self.recipients,
                     html = BODY)

@singletone
class ExceptionManager:
    """
        Для работы модуля должны быть определены следующие переменные:
        
            * **pyramid_rest.request_watcher.use** = True | False - использовать менеджер или нет
            * **pyramid_rest.request_watcher.watch_codes** = [403, 400, 500] - коды ответов, для которых будет сохраняться request|response
            * **pyramid_rest.request_watches.unwatch_codes** = [200] - коды ответов, для которых запретить слежение(имеет более сильный приоритет)
            * **pyramid_rest.request_watcher.handlers** = {200: "db", 500: "email"}
        
        Для работы обработчика email должны быть определены след. переменные:
        
            * **pyramid_rest.request_watcher.handlers.email.recipients** = ["1@mail.ru", "2@mail.ru"]
            * **pyramid_rest.request_watcher.handlers.email.sender** = sender@mail.ru
            
        Менеджер работает следующим образом. Для каждого запроса, код ответа которого удовлетворяет константам, вызывается
        соответствующий обработчик. При этом устанавливается некоторый handler на before-response event(см. :class:`pyramid_rest.events.EventManager`)
        
        .. warning::
        
            Для корректной работы модуля email, должен быть сконфигурирован pyramid_mail!
            
        
    """
    
    HANDLER_MAPPER = {"db": db, 
                      "email": email}
    
    def __init__(self):
        pass
    
    def includeme(self, config):
        try:
            self.use = json.loads(Config()["pyramid_rest.request_watcher.use"])
            self.watch_codes = json.loads(Config()["pyramid_rest.request_watcher.watch_codes"])
            self.unwatch_codes = json.loads(Config()["pyramid_rest.request_watches.unwatch_codes"])
            self.handlers = json.loads(Config()["pyramid_rest.request_watcher.handlers"])
        except Exception as x:
            raise AttributeError("Not all params correctly defined. Full exception: %s\n Trace: %s"%(x, traceback.format_exc()))
        
        if self.use:
            EventManager().bind("before-response", self.handle_response)
    
    def _get_handler(self, string):
        if string not in self.HANDLER_MAPPER:
            raise ValueError("Incorrect handler %s"%string)
        
        return self.HANDLER_MAPPER[string]
    
    def handle_response(self, initiator, request, response):
        """
            Именно эта функция прикручивается к обработчику события **before-response**
        """
        code = request.request.response.status_code
        
        if not self.use:
            return 
        if code not in self.watch_codes:
            return
        if code in self.unwatch_codes:
            return
        
        handlers = self.handlers.get(str(code), None)
        
        for handler in handlers:
            if handler is None:
                Logger().request_manager.error("Code watched, but no handlers found for it. Locals: \n")
                return 
            
            self._get_handler(handler)().handle_response(request, code, response)
        
        
        
        
    
    
#-*- coding: utf-8 -*-
import inspect
import hashlib
import random
from pprint import pformat
import logging
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import pyramid_rest

def singletone(cls, data = {}):
    """
        Реализует паттерн Singletone
    """
    def _c(*a, **k):
        if cls.__name__ not in data:
            data[cls.__name__] = cls(*a, **k)
        return data[cls.__name__]
    _c.__doc__ = cls.__doc__
    _c.__name__ = cls.__name__
    _c.__module__ = cls.__module__
    return _c

def get_class_that_defined_method(meth):
    """
        Получает класс, в котором был определен метод meth
    """
    for cls in inspect.getmro(meth.im_class):
        if meth.__name__ in cls.__dict__: return cls
    return None

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def get_ip(request):
    """
        Получает ip текущего запроса
        
        :param request: текущий инстанс :class:`pyramid_rest.request.Request`
    """
    request = getattr(request, "request", None) or request
    
    if "HTTP_X_REAL_IP" in request:
        return request["HTTP_X_REAL_IP"]
    else:
        return request["REMOTE_ADDR"]
    
def get_or_none(first, *args):
    out = first
    for arg in args:
        try:
            out = getattr(out, arg)
        except:
            return None
    return out

def send_message(request, *a, **k):
    logging.info("Sending message with params: \n%s", pformat(locals()))
    
    if pyramid_rest.config.Config()["mail.send_really"] in ("False", "false"):
        return
    
    MAILER = get_mailer(request)
    
    if "sender" not in k:
        k["sender"] = pyramid_rest.config.Config()["mail.username"]
    
    msg = Message(*a, **k)
    MAILER.send_immediately(msg, fail_silently=False)
    logging.info("Message was sended")

class RandomFromSchema:
    def __init__(self, schema):
        self.schema = schema
        
    def parse(self, schema = None):
        if schema is None: schema = self.schema
        out = {}
        for key, value in schema["properties"].iteritems():
            if key in self.schema.get("required", []):
                if "enum" in value:
                    out[key] = random.choice(value["enum"])
                    continue
                if value["type"] == "object":
                    out[key] = self.parse(value)
                elif value["type"] == "string":
                    if value.get("format", "") == "email":
                        out[key] = self.random_email()
                    else:
                        out[key] = self.random_string()
                elif value["type"] == "integer":
                    out[key] = self.random_int()
                elif value["type"] == "float":
                    out[key] = self.random_float()
                else:
                    out[key] = self.random_string()
        return out
    
    def random_string(self):
        return hashlib.md5(str(random.random())).hexdigest()[:random.randrange(5, 20, 1)]
    
    def random_int(self):
        return random.randrange(1, 10000, 1)
    
    def random_float(self):
        return random.random()*1000
    
    def random_email(self):
        return "%s@%s.ru"%(self.random_string(),
                           self.random_string())
        
        
    
        
        

    
    
    
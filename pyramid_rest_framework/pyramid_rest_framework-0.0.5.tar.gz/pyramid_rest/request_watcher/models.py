#-*- coding: utf-8 -*-
from pyramid_rest.security.models import Base
from pyramid_rest.models_crud import CRUD
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime, Text
import datetime
import json
from sqlalchemy import event

def _handler_json_value_field_set(value):
    try:
        value = json.dumps(value)
    except:
        raise TypeError("Can't dump value %s"%value)
    return value

class Request(Base, CRUD):
    __tablename__ = "_rest_requests"
    id = Column(Integer, primary_key = True)
    host = Column(String(200))
    """Хост на который пришел запрос"""
    path = Column(String(200))
    """Полный путь"""
    ip = Column(String(20))
    """ip запроса"""
    datetime = Column(DateTime)
    """время выполнения запроса"""
    user_id = Column(Integer, ForeignKey("_rest_users.id", ondelete = "cascade"))
    """id юзера, совершившего запрос"""
    request = Column(Text)
    """__dict__ запроса"""
    method = Column(String(10))
    """метод запроса в нижнем регистре"""
    query = Column(Text)
    """GET данные"""
    data = Column(Text)
    """POST body"""
    headers = Column(Text)
    """Список хидеров запроса"""
    
    def __init__(self, *a, **k):
        k["request"] = _handler_json_value_field_set(k["request"])
        k["query"] = _handler_json_value_field_set(k["query"])
        k["data"] = _handler_json_value_field_set(k["data"])
        k["headers"] = _handler_json_value_field_set(k["headers"])
        
        Base.__init__(self, *a, **k)
        self.datetime = datetime.datetime.now()
    
class Response(Base, CRUD):
    __tablename__ = "_rest_responses"
    id = Column(Integer, primary_key = True)
    request_id = Column(Integer, ForeignKey("_rest_requests.id"))
    code = Column(Integer)
    """код ответа"""
    body = Column(Text)
    """текст ответа"""
    
    def __init__(self, *a, **k):
        k["body"] = _handler_json_value_field_set(k["body"])
        
        Base.__init__(self, *a, **k)
    





    
    
    
    
    
    
    
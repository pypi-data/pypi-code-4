#-*- coding: utf-8 -*-
from pyramid_rest.logger import Logger
from pprint import pformat
import json
from pyramid_rest.exceptions import BadRequest

class Request:
    """
        Класс - обертка на pyramid - request. Имеет следующие важные параметры:
        
            * **data** - данные запроса. Имеют формат::
            
                {
                    "query" - GET параметры запроса query
                    "route" - MatchRoute параметры запроса в формате dict
                    "body" - JSON - парсенное тело запроса
                }
                
        Все запросы к api должны подчиняться след. правилам:
        
            * в POST, PUT запросах в body передается json-строка  
            * в GET, DELETE запросах данные передаются как json через параметр query::
            
                
    """
    def __init__(self, request):
        self.request = request
        self.parseBody()
        self.cookies = request.cookies
        self.userid = None
    
    def set_attr(self, key, value):
        setattr(self, key, value)    
    
    def parseBody(self):
        if self.request.body == "": self.request.body = "{}"
        try:
            self.body = json.loads(self.request.body)
        except ValueError:
            raise BadRequest(info = "Couldn't parse json body")
        
        if "query" in self.request.GET:
            try:
                self.query = json.loads(self.request.GET["query"])
            except ValueError:
                raise BadRequest(info = "Query passed, but can't decode")
        else:
            self.query = {}
        
        self.data = {"query": self.query,
                     "route": self.request.matchdict,
                     "body": self.body}
        
        Logger().request.info("Created wrapper for request with data %s", pformat(self.data))
            
    
    def get_method(self):
        """    
            Возвращает метод текущего запроса, get, post, put, delete
        """
        return self.request.method.lower()
    
    
    
    
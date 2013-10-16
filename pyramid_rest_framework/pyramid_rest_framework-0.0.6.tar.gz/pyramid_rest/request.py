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
                    "limit" - ограничение на число записей. Если не передан, устанавливается в 10
                    "offset" - смещение по записям. Если не передано, устанавливается в 0
                    "order" - порядок сортировки. Пример: ["-id", "name"] - сортируется в обратном порядке по id, затем в прямом по name
                }
                
        Все запросы к api должны подчиняться след. правилам:
        
            * в POST, PUT запросах в body передается json-строка  
            * в GET, DELETE запросах данные передаются как json через параметр queryю
            * параметры limit, offset, order передаются через GET

        В процессе жизненного цикла запроса, в него сохраняются след. параметры:
        
            * userid - id юзера, совершившего запрос. None, если юзр не задан
            * bindedTable - ORM класс привязанной таблицы (если isTableBinded == True)
            * count - число записей в запросе (без учета limit и offset)
            * query - выполняемый запрос
            * allowLikeFields - для каких полей таблицы разрешить запрос like в контексте текущего запроса

        Пример корректного GET запроса::

            /user?query={"$or":[{"name":1}, {"email":1}]}&order=["-created"]&limit=10&offset=0
            
                
    """
    def __init__(self, request):
        self.request = request
        self.parseBody()
        self.cookies = request.cookies
        
        self.userid = None
        self.isTableBinded = False
        self.bindedTable = None
        self.count = 0
        self.allowLikeFields = []
    
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
            
        try:
            order = json.loads(self.request.GET.get("order", "[]"))
        except:
            raise BadRequest(info = "Can't decode order")
        
        self.data = {"query": self.query,
                     "route": self.request.matchdict,
                     "body": self.body, 
                     "limit": self.request.GET.get("limit", None),
                     "offset": self.request.GET.get("offset", None), 
                     "order": order}
        
        Logger().request.info("Created wrapper for request with data %s", pformat(self.data))
            
    
    def get_method(self):
        """    
            Возвращает метод текущего запроса, get, post, put, delete
        """
        return self.request.method.lower()
    
    
    
    
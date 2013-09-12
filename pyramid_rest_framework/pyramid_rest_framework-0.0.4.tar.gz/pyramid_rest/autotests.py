#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone, bcolors, RandomFromSchema
from pyramid_rest.logger import Logger
from pprint import pformat, pprint
import requests
import os
import logging
from pyramid_rest.security.models import Users
import transaction
import random
from uuid import uuid4
import json

@singletone
class AutoTestManager(object):
    """
        Класс, для автоматического тестирования REST - методов.
        Хранит информацию о методах в статической переменной META в формате::
        
            {
                resource: <resourceClass name>
                method: <method name>
                url: <route>
                view<resourceView function>
                auth_required: <bool> - требуется ли авторизация
                auth_groups: <list> - необходимые для авторизации группы
                view_name: <str> view.__name__
            }
    """
    META = []
    RESOURCES = []
    HOST = "http://localhost:6543"
    USERS_TABLE = None
    
    def register(self, route, resourceClass):
        """
            Регистрирует ресурс в системе.
            
            :param route: - роут
            :param resourceClass: - класс отнаследованный от :class:`pyramid_rest.resources.Resource`
        """
        self.RESOURCES += resourceClass.__name__
        for method, resourceView in resourceClass.__dict__.iteritems():
            if method in ("get", "post", "delete",
                          "get_object",
                          "put_object",
                          "delete_object"):
                if "object" in method:
                    route = os.path.join(route, str(1))
                item = self.search(method = method, resource = resourceClass.__name__)
                if len(item) == 1:
                    item[0]["url"] = route
                elif len(item) == 0:
                    self.META += [{"resource": resourceClass.__name__,
                                    "method": method,
                                    "url": route,
                                    "view": resourceView,
                                    "auth_required": False,
                                    "auth_groups":[],
                                    "view_name": resourceView.__name__,
                                    "validated": False,
                                    "validated_schema": {},
                                    "data":{}}]
                else:
                    raise ValueError("Can't be more than 1 item")
                
        Logger().main.info("Registered class %s for autotesting.", resourceClass.__name__)
    
    def add_or_change(self, data):
        meta_item = self.search(resource = data["resource"],
                       method = data["method"])
        if len(meta_item) > 0:
            meta_item[0].update(data)
        else:
            self.META += [data]
            
    
    def search(self, **keys):
        """
            Отбирает информацию о ресурсах в META согласно переданным key-value параметрам
        """
        out = []
        logging.info("Searching in META = %s with keys %s", pformat(self.META), pformat(keys))
        for item in self.META:
            GOOD = True
            Logger().main.info("Searching into %s", item)
            for key, value in keys.iteritems():
                if item.get(key)  !=  value:
                    Logger().main.info("Checking key %s: pair %s = %s", key, item[key], value)
                    GOOD = False
                    break
            if GOOD:
                out += [item]
        return out
                    
    
    def applySchema(self, view):
        pass
    
    def _run_one(self, meta_item):
        method = meta_item["method"]
        url = meta_item["url"]
        
        COOKIES = {}
        BODY = {}
        QUERY = {}
        ROUTE = {}
        
        METHOD = method.replace("_object", "").upper()
        
        if meta_item.get("auth_required", False):
            with transaction.manager:
                sid = self.USERS_TABLE(email = str(uuid4()),
                      password = 1,
                      group = random.choice(list(['main']) + list(meta_item["auth_groups"])))._add().add_session().sid
            COOKIES["SID"] = sid
        
        if meta_item.get("validated", False):
            body_schema = meta_item["validated_schema"].get("body", None)
            if body_schema:
                BODY = RandomFromSchema(body_schema).parse()
                
            query_schema = meta_item["validated_schema"].get("query", None)
            if query_schema:
                QUERY = RandomFromSchema(query_schema).parse()
                
            route_schema = meta_item["validated_schema"].get("route", None)
            if route_schema:
                ROUTE = RandomFromSchema(route_schema).parse()
        
        BODY.update(meta_item.get("data",{}).get("body", {}))
        COOKIES.update(meta_item.get("data",{}).get("cookies", {}))
            
        print "DATA", pformat(BODY)
        
        session = requests.Session()
        request = requests.Request(METHOD, 
                                   self.HOST+url,
                                   cookies = COOKIES,
                                   data = json.dumps(BODY)).prepare()
        response = session.send(request)
        return response
            
    
    def run(self):
        """
            Запускает тесты
        """
        logging.error("Run tests, META: %s", pformat(self.META))
        COUNT = {}
        TOTAL = 0
        for meta in self.META:
            response = self._run_one(meta)
            
            if response.status_code == 200:
                print bcolors.OKGREEN
                  
            elif response.status_code in (403, 400):
                print bcolors.WARNING
                
            elif response.status_code == 500:
                print bcolors.FAIL
            
            pprint({"test": meta, 
                    "code": response.status_code,
                    "response": response.text})
            
            if response.status_code not in COUNT: COUNT[response.status_code] = 0
            COUNT[response.status_code] += 1
            TOTAL += 1

            print bcolors.ENDC
            
        print bcolors.OKBLUE, "TOTAL: %s, COUNT BY CODES: %s"%(TOTAL, pformat(COUNT)), bcolors.ENDC
            

class TestDecorator:
    """
        Изменяет параметры соотв. записи в AutoTestManager
    """
    def __init__(self, data, cls, expectedResponse = None):
        self.data = data
        self.expected = expectedResponse
        self.cls = cls
        
        
    def __call__(self, resource_view):
        
        AutoTestManager().add_or_change({"data":self.data,
                                         "resource": self.cls,
                                         "method": resource_view.__name__,
                                         "view_name": resource_view.__name__})
        
        return resource_view
        
        
    


        
        
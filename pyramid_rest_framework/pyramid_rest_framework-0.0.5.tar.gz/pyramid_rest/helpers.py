#-*- coding: utf-8 -*-
import inspect
import hashlib
import random
from pprint import pprint, pformat
from sqlalchemy.sql.expression import or_, desc
import logging
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

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
    MAILER = get_mailer(request)
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
        
class QueryParser:
    """
        Выполняет парсинг MongoDB - подобного запроса.
        
        Описание формата::
        
            {
                "query": <QueryParser query>
                "order": ["field1", "-field2"]
                "limit": <integer>
                "offset": <integer>
            }
            
        Где:
        
            * **query** - Запрос
            * **order** - порядок сортировки. В данном примере, сортировка выполняется по field1 в прямом порядке, по field2 в обратном порядке с приоритетом field1, field2.
            * **limit** - Число записей (для пагинации)
            * **offset** - смещение
        
        .. note:: 
        
            Например, limit = 10, offset = 10 вернет 10 записей, начиная с 20-й.
            
        **Формат запроса**:
        
            * Фильтрация field=value::
            
                {field: value}
                
            * Фильтрация field > value::
            
                {field: {"$gt":value}}
             
            * Фильтрация field < value::
            
                {field: {"$lt":value}}
                
            * Фильтрация field >= value::
            
                {field: {"$gte":value}}
                
            * Фильтрация field <= value::
            
                {field: {"$lte":value}}
            
            * Фильтрация field in [value1, value2, ...]::
            
                {field: {"$in": [value1, ...]}}
                
            * Фильтрация or:
            
                {"$or": [<Query1>, ...]}
                
            Где <Query1>, ... - запросы указанного формата
            
            * Фильтрация and:
            
                {key1: value1, key2:value2, ...}
            
    """
    
    def __init__(self, table, sqlalchemy_query, query_object):
        self.db = sqlalchemy_query
        self.table = table
        
        self.query = query_object.get("query", {})
        self.order = query_object.get("order", [])
        self.limit = query_object.get("limit", None)
        self.offset = query_object.get("offset", None)
        
        logging.getLogger("decorators").error("Initialized queryParser instance with params: query = %s\norder = %s\nlimit = %s\noffset = %s", 
                                 self.query, 
                                 self.order, 
                                 self.limit, 
                                 self.offset)
    
    def _get_ordering(self):
        ORDERING = []
        for key in self.order:
            if key[0] != "-":
                ORDERING += [getattr(self.table, key)]
            else:
                key = key[1:]
                ORDERING += [desc(getattr(self.table, key))]
        return ORDERING
    
    def _parse(self, query = None):
        if query is None: query = self.query
        
        FILTERING_OBJECT = []
        
        if isinstance(query, dict):
            for key, value in query.iteritems():
                if key not in ["$or", ]:
                    if not isinstance(value, dict):
                        FILTERING_OBJECT += [getattr(self.table, key) == value]
                    else:
                        if len(value)!=1:
                            raise TypeError("Incorrect query format")
                        command = value.keys()[0]
                        command_data = value[command]
                        
                        if command == "$in":
                            FILTERING_OBJECT += [getattr(getattr(self.table, key), "in_")(command_data)]
                        
                        elif command == "$lt":
                            FILTERING_OBJECT += [getattr(self.table, key) < command_data]
                            
                        elif command == "$gt":
                            FILTERING_OBJECT += [getattr(self.table, key) > command_data]
                        
                        elif command == "$lte":
                            FILTERING_OBJECT += [getattr(self.table, key) <= command_data]
                            
                        elif command == "$gte":
                            FILTERING_OBJECT += [getattr(self.table, key) >= command_data]
                        
                        else:
                            raise TypeError("Incorrect format")
                            
                elif key == "$or":
                    OR = []
                    for search_pair in value:
                        OR += self._parse(search_pair)
                    FILTERING_OBJECT += [or_(*OR)]
        else:
            raise TypeError("Incorrect query format")
                
        return FILTERING_OBJECT
    
    def execute(self):
        QUERY = self._parse()
        self.db = self.db.filter(*QUERY).order_by(*self._get_ordering())
        
        if self.limit:
            self.db = self.db.limit(self.limit)
        if self.offset:
            self.db = self.db.offset(self.offset)
        
        logging.error("Executing, %s", self.db)
        
        return self.db
        
    
        
        

    
    
    
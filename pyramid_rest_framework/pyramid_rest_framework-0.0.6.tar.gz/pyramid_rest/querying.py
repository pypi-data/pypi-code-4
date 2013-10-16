#-*- coding: utf-8 -*-
from sqlalchemy.sql.expression import or_, desc, Alias
from pyramid_rest.config import Config
from pyramid_rest.logger import Logger
import logging
from pyramid_rest.exceptions import BadRequest, ExceptionInterface
import traceback

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
                
            * Фильтрация or::
            
                {"$or": [<Query1>, ...]}
                
            Где <Query1>, ... - запросы указанного формата
            
            * Фильтрация and::
            
                {key1: value1, key2:value2, ...}
            
            * Фильтрация like::
            
                {field: {"$like": value}}
                
            .. warning::
                
                По умолчанию like фильтрация запрещена для всех полей. Чтобы разрешить like фильтрацию 
                для некоторых полей некоторого роута, надо добавить названия этих полей в **request.allowLikeFields**
                с помощью :class:`pyramid_rest.decorators.CustomValidators.Exec`
            
        .. note::
        
            По умолчанию, сервер отдает данные с limit = **pyramid_rest.querying.default_limit**. Если этот параметр не задан, вернется 10 записей.
            
    """
    
    def __init__(self, table, sqlalchemy_query, query_object, request):
        self.db = sqlalchemy_query
        self.table = table
        
        self.request = request
        
        self.query = query_object.get("query", {})
        self.order = query_object.get("order", [])
        self.limit = query_object.get("limit", None) or Config()["pyramid_rest.querying.default_limit"] or 10
        self.offset = query_object.get("offset", None) or 0
        
        Logger().querying.info("Initialized queryParser instance with params: query = %s\norder = %s\nlimit = %s\noffset = %s", 
                                 self.query, 
                                 self.order, 
                                 self.limit, 
                                 self.offset)
        
    def _getattr(self, name):
        if isinstance(self.table, Alias):
            return getattr(self.table.c, name)
        else:
            return getattr(self.table, name)
    
    def _get_ordering(self):
        ORDERING = []
        for key in self.order:
            if key[0] != "-":
                ORDERING += [self._getattr(key)]
            else:
                key = key[1:]
                ORDERING += [desc(self._getattr(key))]
        return ORDERING
    
    def _parse(self, query = None):
        if query is None: query = self.query
        
        FILTERING_OBJECT = []
        
        if isinstance(query, dict):
            for key, value in query.iteritems():
                if key not in ["$or", ]:
                    if not isinstance(value, dict):
                        FILTERING_OBJECT += [self._getattr(key) == value]
                    else:
                        if len(value)!=1:
                            raise TypeError("Incorrect query format")
                        command = value.keys()[0]
                        command_data = value[command]
                        
                        if command == "$in":
                            FILTERING_OBJECT += [getattr(self._getattr(key), "in_")(command_data)]
                        
                        elif command == "$lt":
                            FILTERING_OBJECT += [self._getattr(key) < command_data]
                            
                        elif command == "$gt":
                            FILTERING_OBJECT += [self._getattr(key) > command_data]
                        
                        elif command == "$lte":
                            FILTERING_OBJECT += [self._getattr(key) <= command_data]
                            
                        elif command == "$gte":
                            FILTERING_OBJECT += [self._getattr(key) >= command_data]
                        elif command == "$like":
                            if key in self.request.allowLikeFields:
                                FILTERING_OBJECT += [self._getattr(key).like(command_data)]
                            else:
                                raise BadRequest(info = "$like syntax is not allowed in current context")
                        else:
                            raise BadRequest(info = "Incorrect query format")
                            
                elif key == "$or":
                    OR = []
                    for search_pair in value:
                        OR += self._parse(search_pair)
                    FILTERING_OBJECT += [or_(*OR)]
        else:
            raise TypeError("Incorrect query format")
                
        return FILTERING_OBJECT
    
    def execute(self):
        try:
            QUERY = self._parse()
        except ExceptionInterface as x:
            raise x
        except:
            Logger().decorators.error("Error in parsing query. Original trace: %s", 
                                      traceback.format_exc())
            raise BadRequest(info = "Can't parse query")
        
        self.db = self.db.filter(*QUERY).order_by(*self._get_ordering())
        
        self.count = self.db.count()
        
        if self.limit:
            self.db = self.db.limit(self.limit)
        if self.offset:
            self.db = self.db.offset(self.offset)
        
        Logger().querying.info("Executing, %s", self.db)
        
        return self.db
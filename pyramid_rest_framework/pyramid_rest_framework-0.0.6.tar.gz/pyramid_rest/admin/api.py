#-*- coding: utf-8 -*-
import logging
from pyramid_rest.helpers import singletone
from pyramid_rest.decorators import registerResource, bindTable, customValidator,\
    CustomValidators, ApplyMapper
from pyramid_rest.resources import Resource
from pyramid_rest.security.decorators import AllowToGroups
import os
from pprint import pprint, pformat
import json
from pyramid_rest.logger import Logger

def get_or_none(cls, *attrs):
    res = None
    for attr in attrs:
        try:
            res = getattr(cls, attr)
        except:
            res = None
            break
    return res


@singletone
class TablesManager:
    TABLES = []
    
    def __init__(self, app = None): self.api = app

    def _parse_column_type(self, string):
        return {"INTEGER": "integer",
                "FLOAT": "float",
                "DATETIME": "datetime",
                "DATE": "date",
                "BOOLEAN": "boolean",
                "TEXT": "text"}.get(string, "string")

    def _parse_column_info(self, column):
        OUT = {"primary_key": column.primary_key,
                "autoincrement": column.autoincrement,
                "type": self._parse_column_type(str(column.type)),
                "unique": column.unique,
                "nullable": column.nullable,
                #"default": column.default, 
                "foreign_key": False}
        
        if column.foreign_keys:
            if len(column.foreign_keys) > 0:
                Logger().admin.info(u"Не поддерживаются внешние ключи более чем на 1 таблицу: %s", column.foreign_keys)
            OUT["foreign_key"] = True
            OUT["foreign_key_column"] = list(column.foreign_keys)[0]._colspec
        
        return OUT

    def add_table(self, tableClass):
        """
            Добавляет одну таблицу в менеджер
        """
        
        
        columns_dict = tableClass.__table__._columns._data

        COLUMNS_INFO = {}

        for key in columns_dict.keys():
            COLUMNS_INFO[key] = self._parse_column_info(columns_dict[key])

        self.TABLES.append({"name": tableClass.__name__.lower(),
                            "tableName": tableClass.__table__.fullname,
                            "columns_names": COLUMNS_INFO.keys(),
                            "columns": COLUMNS_INFO,
                            "table_route": os.path.join(self.api.route_prefix, tableClass.__name__.lower()),
                            "meta":  get_or_none(tableClass, "__meta__")})
    
    def get(self, **k):
        """
            Возвращает таблицы, удовлетворяющие переданным параметрам **k
        """
        OUT = []
        
        for table in self.TABLES:
            IS_GOOD = True
            if k:
                for key, value in k.iteritems():
                    if table[key] != value:
                        IS_GOOD = False
                        continue
            if IS_GOOD: OUT += [table]
        return OUT

class fullTableDataMapper:
    def __init__(self, tableClass):
        self.cls = tableClass 
        
    def __call__(self, request, el):
        def is_jsonable(smth):
            try:
                json.dumps(smth)
                return True
            except TypeError:
                Logger().main.warning("Value %s isn't JSON serializable", smth)
                return False
            
        out = {}
        db_item = self.cls._get(id = el["id"])
        Logger().admin.info("Map elem %s with columns %s", pformat(el), pformat(TablesManager().get(name = self.cls.__name__.lower())[0]["columns_names"]))
        for column in TablesManager().get(name = self.cls.__name__.lower())[0]["columns_names"]:
            value = getattr(db_item, column)
            if not is_jsonable(value):
                value = unicode(value)
            out[column] = value
        return out
        
@singletone
class Api(object):
    
    TABLES = []
    """
        Тут хранятся инстансы **WrappedTableClass**
    """
    def __init__(self):
        self.route_prefix = "/rest_admin"
        
        TablesManager(self)
        
    
    def __call__(self, tableClass):
        self.TABLES.append(tableClass)
        self.register_routes(tableClass)
        return tableClass
    
    def register_routes(self, tableClass):
        TablesManager().add_table(tableClass)
        class tableResource(Resource):
            
            @AllowToGroups("admin")
            @ApplyMapper(fullTableDataMapper(tableClass))
            @bindTable(tableClass)
            def get(self, request, data):
                pass 
            
            @AllowToGroups("admin")
            @ApplyMapper(fullTableDataMapper(tableClass))
            @bindTable(tableClass)
            def post(self, request, data):
                pass 
            
            @AllowToGroups("admin")
            @ApplyMapper(fullTableDataMapper(tableClass))
            @bindTable(tableClass)
            def delete(self, request, data):
                pass 
            
            @AllowToGroups("admin")
            @ApplyMapper(fullTableDataMapper(tableClass))
            @bindTable(tableClass)
            def put_object(self, request, data):
                pass 
            
            @AllowToGroups("admin")
            @ApplyMapper(fullTableDataMapper(tableClass))
            @bindTable(tableClass)
            def get_object(self, request, data):
                pass 
            
            @AllowToGroups("admin")
            @ApplyMapper(fullTableDataMapper(tableClass))
            @bindTable(tableClass)
            def delete_object(self, request, data):
                pass 
            
        tableResource.__name__ = "_rest_admin_"+tableClass.__name__
        tableResource = registerResource("/rest_admin/tables/%s"%tableClass.__name__.lower())(tableResource)
    
    def includeme(self, config):
        """
            Используется для подключения Api к серверу приложения.
            Добавляет необходимые роуты для сервера.
        """
        config.add_jinja2_search_path("pyramid_rest:templates")
        config.add_route("admin_index", self.route_prefix, view = lambda request: {}, renderer = "index.html.jinja2")
        config.add_route("_rest_admin_login", "/rest_admin/login", view = lambda request: {}, renderer = "login.html.jinja2")
        config.add_static_view("admin_static", "pyramid_rest:static")
        
        
        
        
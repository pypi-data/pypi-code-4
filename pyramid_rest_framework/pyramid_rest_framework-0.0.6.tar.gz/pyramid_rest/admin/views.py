#-*- coding: utf-8 -*-
from pyramid_rest.resources import Resource
from pyramid_rest.security.decorators import AllowToGroups
from pyramid_rest.admin.api import Api, TablesManager
import os
from pyramid_rest.helpers import get_or_none
from pyramid_rest.decorators import registerResource, validateRequest
from pyramid.view import view_config
import transaction
from pyramid_rest.security.models import Users
from pyramid_rest.exceptions import Forbidden
from pprint import pformat

def api_index(request):
    return {}

def login(request):
    return {}

@registerResource("/rest_admin/get_tables")
class TableMetaResource(Resource):
    u"""
            Возвращает представление, возвращающее информацию о зарегестрированных таблицах. Для полноты 
            у всех таблиц можно устанавливать дополнительно атрибут **__meta__**::
            
                __meta__ = {
                                group: группа в которую относится таблица
                                description: описание таблицы
                            }
            
            * **Формат запроса: **
            
                * **url** <admin_prefix>/get_tables
            
            * **Формат ответа**::
            
                [{'class': <class 'pyramid_rest.request_watcher.models.Request'>,
                  'columns': {'data': {'autoincrement': True,
                                       'default': None,
                                       'foreign_key': False,
                                       'nullable': True,
                                       'primary_key': False,
                                       'type': 'string',
                                       'unique': None},
                              'datetime': {'autoincrement': True,
                                           'default': None,
                                           'foreign_key': False,
                                           'nullable': True,
                                           'primary_key': False,
                                           'type': 'string',
                                           'unique': None},
                              'headers': {'autoincrement': True,
                                          'default': None,
                                          'foreign_key': False,
                                          'nullable': True,
                                          'primary_key': False,
                                          'type': 'string',
                                          'unique': None},
                              'host': {'autoincrement': True,
                                       'default': None,
                                       'foreign_key': False,
                                       'nullable': True,
                                       'primary_key': False,
                                       'type': 'string',
                                       'unique': None},
                              'id': {'autoincrement': True,
                                     'default': None,
                                     'foreign_key': False,
                                     'nullable': False,
                                     'primary_key': True,
                                     'type': 'string',
                                     'unique': None},
                              'ip': {'autoincrement': True,
                                     'default': None,
                                     'foreign_key': False,
                                     'nullable': True,
                                     'primary_key': False,
                                     'type': 'string',
                                     'unique': None},
                              'method': {'autoincrement': True,
                                         'default': None,
                                         'foreign_key': False,
                                         'nullable': True,
                                         'primary_key': False,
                                         'type': 'string',
                                         'unique': None},
                              'path': {'autoincrement': True,
                                       'default': None,
                                       'foreign_key': False,
                                       'nullable': True,
                                       'primary_key': False,
                                       'type': 'string',
                                       'unique': None},
                              'query': {'autoincrement': True,
                                        'default': None,
                                        'foreign_key': False,
                                        'nullable': True,
                                        'primary_key': False,
                                        'type': 'string',
                                        'unique': None},
                              'request': {'autoincrement': True,
                                          'default': None,
                                          'foreign_key': False,
                                          'nullable': True,
                                          'primary_key': False,
                                          'type': 'string',
                                          'unique': None},
                              'user_id': {'autoincrement': True,
                                          'default': None,
                                          'foreign_key': True,
                                          'foreign_key_column': '_rest_users.id',
                                          'nullable': True,
                                          'primary_key': False,
                                          'type': 'string',
                                          'unique': None}},
                  'columns_names': ['id',
                                    'host',
                                    'path',
                                    'ip',
                                    'datetime',
                                    'user_id',
                                    'request',
                                    'method',
                                    'query',
                                    'data',
                                    'headers'],
                  'meta': None,
                  'name': 'request',
                  'tableName': '_rest_requests',
                  'table_route': '/rest_admin/request'}]
            
    """
    @AllowToGroups("admin")
    def get(self, request):
        api = Api()
        return TablesManager().get()
    
            
@registerResource("/rest_admin/auth")
class Auth(Resource):
    
    @validateRequest({"body": {"type":"object",
                               "properties": {"email": {"type": "string", 
                                                        "format": "email"},
                                              "password": {"type": "string"}},
                               "required": ["email", "password"]}})
    def post(self, request):
        with transaction.manager:
            db_user = Users._get(email = request.data["body"]["email"])
            
            if db_user is None:
                raise Forbidden()
            
            if not db_user.check_password(request.data["body"]["password"]):
                raise Forbidden()
            
            if db_user.group != "admin":
                raise Forbidden()
            
            request.request.response.set_cookie("SID", db_user.add_session().sid)
            
        return {}
        
        
    
        
        
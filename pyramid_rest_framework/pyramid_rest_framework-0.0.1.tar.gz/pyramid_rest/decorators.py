#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone, QueryParser
import os
from pyramid_rest.logger import Logger
from pprint import pformat, pprint
from jsonschema.validators import Draft3Validator, ErrorTree, Draft4Validator
from pyramid_rest.exceptions import ValidationError, UnknownError, BadRequest
import transaction
import sqlahelper
from bsddb import db
from pyramid_rest.autotests import AutoTestManager

class registerResource:
    """
        Регистрирует роуты для классов :class:`pyramid_rest.resources.Resource`. Пример использования::
        
            @registerResource("/users")
            class UserViews(Resource):
                ...
        
        Сам класс лишь сохраняет роуты в self.routes_meta, которые потом будут зарегестрированы в :class:`pyramid_rest.app.App`
        
        При этом будут зарегестрированы 2 роута:
        
            * /users - табличный
            * /users/{id} - объектный.
            
        :param url: url роута
        
        .. note::
        
            При использовании декоратора, к документации ресурса автоматически дописывается следующая информация::
            
                Класс - Resource. Зарегестрированные представления:

                        * table URI: <uri>
                        * object URI: <uri>
                        
                    Доступные методы:
                    
                        <allowed_methods>
            
            * table URI - URI для таблицы
            * object URI - URI для одного объекта
            * allowed_methods - доступные методы. Методы  приставкой _object (f.e. get_object) - это методы доступные для object URI, остальные для table URI
    """
    routes_meta = []
    def __init__(self, url):
        self.url = url
    
    def __call__(self, resourceClass):
        routes = [{"name": resourceClass.__name__,
                 "url": self.url,
                 "resourceClass": resourceClass}]
        
        Logger().decorators.info("Adding route_meta: \n%s", 
                                 pformat(routes[0]))
        self.routes_meta += routes
        
        resourceClass.__doc__ = resourceClass.__doc__ or u""
        resourceClass.__doc__ += u"""\n
Класс - Resource. Зарегестрированные представления:

    * table URI: **%s**
    * object URI: **%s**
    
Доступные методы::

    %s
    
        """%(self.url, os.path.join(self.url, "{id}"),
             pformat([x for x in resourceClass.__dict__.keys() if x in \
                        ["get", "post", "put", "delete", "get_object",
                         "post_object", "put_object", "delete_object"]]))
        
        AutoTestManager().register(self.url, resourceClass)
        
        return resourceClass
    
    @staticmethod
    def register(app):
        """
            Выполняет регистрацию роутов в системе.
            
            :param app: :class:`pyramid_rest.app.App` инстанс
        """
        app.logger.decorators.info("Registering routes from route meta. Routes: \n%s",
            pformat(registerResource.routes_meta))
        for routeMeta in registerResource.routes_meta:
            app.server.add_route(routeMeta["name"] + "-table", 
                                 routeMeta["url"], 
                                 routeMeta["resourceClass"](app).get_table_view())
            
            app.server.add_route(routeMeta["name"] + "-object", 
                                 os.path.join(routeMeta["url"], "{id}"), 
                                 routeMeta["resourceClass"](app).get_object_view())
            
            app.resources[routeMeta["resourceClass"].__name__] = {"class": routeMeta["resourceClass"],
                                                                  "url": routeMeta["url"]}

class customValidator:
    """
        Декоратор, позволяет произвольным образом провалидировать запрос к resource - представлению.
        
        :param function: Функция - валидатор. Принимает на вход экземпляр :class:`pyramid_rest.request.Request`. В случае ошибки валидации генерит инстанс :class:`pyramid_rest.exceptions.ValidationError`
    """ 
    def __init__(self, function):
        self.function = function
    
    def __call__(self, resource_view):
        def _callback(self_resource):
            self.function(self_resource.request)
            return resource_view(self_resource)
        _callback.__doc__ = resource_view.__doc__
        _callback.__name__ = resource_view.__name__
        _callback.__module__ = resource_view.__module__
        return _callback

class validateRequest:
    """
        Проводит валидацию запроса согласно переданной schema
        
        * **Формат schema**::
        
            {
                "query": <JSON schema для валидации query>
                "body": <JSON schema для валидации body>
                "route: <JSON schema для валидации route-параметров>
            }
        
        .. warning::
        
            В целях безопасности, к каждой Schema добавляется параметр additionalProperties: false.
        
        * В случае ошибки валидации генерится сообщение в формате::
        
            {
                "info": 
                    {
                        "body":         #ошибки в валидации body
                            {
                                "key2": {        #поле
                                    "path": ["key2"],     #путь до этого поля в объекте, набор ключей
                                    "message": "u'0' is not one of ['1', '2']"    #сообщение об ошибке
                                },
                                "key1": {
                                    "path": ["key1"], 
                                    "message": "u'1' is not of type 'integer'"
                                }
                            }, 
                        "query": {},     #ошибки в валидации query
                        "route": {}    #ошибки в валидации route-параметров
                    }, 
                "code": 400, 
                "name": "ValidationError"
            }
            
        * В случае если параметр **additionalProperties** False, и переданы лишние поля, возвращается::
        
            {
                info: "Additional properties are not allowed (u'key' was unexpected)"
                code: 400
                name: "ValidationError"
            }
            
        * Пример использования декоратора::
        
            @validateRequest({"body": {
                "type": "object",
                "properties": {
                    "key1": {
                        "type": "integer",
                        "required": True
                    },
                    "key2": {
                        "type": "string",
                        "required": False,
                        "enum": ["1","2"]
                    }
                }}})
            def post(self):
                print "IN POST!"
                return {"response": self.request.data}
    """
    resources_meta = []
    def __init__(self, schema, cls = None):
        self.schema = schema
        if "query" in schema: 
            schema["query"]["additionalProperties"] = False
            self.querySchema = schema["query"]
        else: self.querySchema = None
        
        if "body" in schema: 
            schema["body"]["additionalProperties"] = False
            self.bodySchema = schema["body"]
        else: self.bodySchema = None
        
        if "route" in schema: 
            schema["route"]["additionalProperties"] = False
            self.routeSchema = schema["route"]
        else: self.routeSchema = None
        
        self.cls = cls
    
    def _validateSchema(self, schema, data):
        validator = Draft4Validator(schema)
        
        Logger().decorators.info("Validating data %s with schema %s", pformat(data), pformat(schema))
        
        errors = {}
        
        for error in validator.iter_errors(data):
            print error.path, error.message, "\tError\n\n\n"
            if len(error.path)>0:
                errors[list(error.path)[-1]] = {"message": error.message,
                                                "path": list(error.path)}
            else:
                raise ValidationError(info = error.message)
            
        return errors
    
    def __call__(self, resource_view):
        out = customValidator(self.validate)(resource_view)
        out.__doc__ = out.__doc__ or ""
        out.__doc__ += u"""
    * Schema для валидации метода::
    
        %s
    """%(pformat(self.schema))
    
        
        if self.cls:
            autotest_meta = AutoTestManager().search(resource = self.cls,
                                                     method = resource_view.__name__,
                                                     view_name = resource_view.__name__)
            if len(autotest_meta) > 0:
                for meta_item in autotest_meta:
                    meta_item["validated"] = True
                    meta_item["validated_schema"] = self.schema
            else:
                AutoTestManager().META += [{"resource": self.cls,
                                            "method": resource_view.__name__,
                                            "url": None,
                                            "view": resource_view,
                                            "auth_required": False,
                                            "auth_groups":[],
                                            "view_name": resource_view.__name__,
                                            "validated": True,
                                            "validated_schema": self.schema}]
    
        return out
    
    def validate(self, rest_request):
        Logger().decorators.info("Validating request")
        errors = {}
        
        if self.querySchema:
            queryErrors = self._validateSchema(self.querySchema, rest_request.data["query"])
        else:
            queryErrors = False
        
        if self.bodySchema:
            bodyErrors = self._validateSchema(self.bodySchema, rest_request.data["body"])
        else:
            bodyErrors = False
        
        if self.routeSchema:
            routeErrors = self._validateSchema(self.routeSchema, rest_request.data["route"])
        else:
            routeErrors = False
            
        if queryErrors or routeErrors or bodyErrors:
            raise ValidationError(info = {"query": queryErrors or {},
                                          "body": bodyErrors or {},
                                          "route": routeErrors or {}})

class CustomValidators:
    """
        Набор полезных валидаторов. Используется вместе с :class:`pyramid_rest.decorators.customValidator`. Пример::
        
            @customValidator(CustomValidators.SomeValidator)
            def get(self):
                ...
    """
    
    class UniqueField:
        """Декоратор, проверяет уникальность поля field в таблице Table"""
        def __init__(self, table, field):
            self.table = table
            self.field = field
            
        def __call__(self, request):
            with transaction.manager:
                if not self.table._get(**{self.field: request.data["body"][self.field]}) is None:
                    raise ValidationError(info = {"body": {self.field: {"message": "Not unique value"}}})
                
    class DisallowFields:
        """
            Фильтрует поля в запросе. Убирает из запроса поля, которые переданы.
            
            * fields - поля для фильтрации.::
            
                {
                    "query": [field1, field2, ...]
                    "body": [field1, field2, ...]
                    "options": [field1, field2, ...]
                }
        """
        def __init__(self, fields):
            self.fields = fields
            
        def __call__(self, request):
            for key, array in self.fields.iteritems():
                BAD_KEYS = []
                for field, value in request.data.get(key).iteritems():
                    if field in array:
                        BAD_KEYS += [field]
                        
                for field in BAD_KEYS: del request.data.get(key)[field]
            
    class AllowFields:
        """
            Фильтрует поля в запросе.
            
            * fields - поля для фильтрации.::
            
                {
                    "query": [field1, field2, ...]
                    "body": [field1, field2, ...]
                    "options": [field1, field2, ...]
                }
            
            После этого декоратора, объект request.data содержит только указанные поля
        """
        def __init__(self, fields):
            self.fields = fields
            
        def __call__(self, request):
            for key, array in self.fields.iteritems():
                BAD_KEYS = []
                for field, value in request.data.get(key).iteritems():
                    if field not in array:
                        BAD_KEYS += [field]
                        
                for field in BAD_KEYS: del request.data.get(key)[field]
        
         
    class ForeignKey:
        """
            Реализует ограничение типа "Внешний ключ"
            
            :param field: Имя поля в запросе.
            :param table: Таблица, на которую накидываем внешний ключ
            :param column: Имя колонки - ключа в таблице. 
            :param query: Фильтр запроса. Для ForeignKey отбираются только значения, отфильтрованные по этому запросу.
            :param notnull: default = False. Разрешить NULL значения для ключа
            
            .. note::
            
                Рассматриваются только поля из body!
            
            Пример::
            
                @ForeignKey("ref_owner_id", Users, Users.id, {"ref_is_manager": 1})
                def post(...)
                
            В примере, значение поля "ref_owner_id" должно быть одним из id Юзеров у которых параметр "ref_is_manager" = 1
            
        """
        def __init__(self, field, table, column, query = {}, notnull = False):
            self.field = field
            self.table = table
            self.column = column
            self.query = query
            self.notnull = notnull
            
        def __call__(self, request):
            field_data = request.data["body"].get(self.field, None)
            
            with transaction.manager:
                if field_data is None:
                    if self.notnull:
                        raise ValidationError("Null values for key %s not allowed!"%(self.column))
                    else:
                        return
                
                Logger().decorators.info("Validating foreign key constraint. Params: %s", 
                                         pformat(locals()))
                
                db_item = self.table._filter(getattr(self.table, self.column) == field_data)
                
                for key, value in self.query.iteritems():
                    db_item = db_item.filter(getattr(self.table, key) == value)
                
                if db_item.first() is None:
                    raise ValidationError(info = {"errors": {self.field: {"message": "Incorrect foreign key value."}}})

class ApplyMapper:
    u"""
        Декоратор на ресурсные представления. Применяет переданную функцию **mapper** ко всем элементам результата декорируемой функции.
        
        :param mapper: Функция.
        
        .. note::
        
            Декорируемая функция принимает экземпляр :class:`pyramid_rest.request.Request` первым параметром и объект маппируемой коллекции вторым.
        
        .. warning::
        
            Маппирование производится внутри транзакции. Дополнительные транзакции внутри функции **mapper** не нужны!
    """
    def __init__(self, mapper):
        self.mapper = mapper
        
    def __call__(self, resource_view):
        def _callback(self_request):
            data = resource_view(self_request)
            
            with transaction.manager:
                try:
                    if type(data) is list:
                        return map(lambda x: self.mapper(self_request, x), data)
                    elif type(data) is dict:
                        return self.mapper(self_request, data)
                    else:
                        Logger().decorators.warning("Incorrect value passed to mapper: %s", pformat(locals()))
                except Exception as x:
                    Logger().decorators.error("Error while mapping: %s\nLocals: %s", x, pformat(locals()))
                    return data
        
        _callback.__doc__ = resource_view.__doc__ or ""
        
        _callback.__doc__ += u"""
        
        .. warning::
             **Метод маппируется!**. 
        
        Подробнее о маппинге метода:
        %s
        
        """%self.mapper.__doc__
        
        _callback.__name__ = resource_view.__name__
        _callback.__module__ = resource_view.__module__
        
        return _callback
        
            
            
class bindTable:
    """
        Декоратор, выполняет привязку таблицы к resource - методу.
        
        :param sqlalchemy_table: sqlalchemy table class
        
        В зависимости от имени декорируемого метода, вызывается соответствующий метод класса. 
        
        .. warning::
        
            Этот декоратор должен использоваться **последним** в цепочке декораторов!
            
        Функция, которую декорирует этот декоратор, обязана принимать два параметра::
            
            @bindTable(SomeTable)
            def func(self, data):
                pass
                
        Где self - инстанс :class:`pyramid_rest.resources.Resource`, data - значение, возвращаемое соответствующим методом bindTable.s
    """
    def __init__(self, sqlalchemy_table):
        self.type = type
        self.table = sqlalchemy_table
        
    def __call__(self, resource_view):
        def _callback(self_resource):
            if not hasattr(self, resource_view.__name__):
                raise UnknownError(info = "No views with name %s"%resource_view.__name__)
            
            bind_output_data = getattr(self, resource_view.__name__)(self_resource)
            resource_output_data = resource_view(self_resource, bind_output_data)
            
            if resource_output_data is None:
                resource_output_data = bind_output_data
            
            return resource_output_data
        
        _callback.__doc__ = resource_view.__doc__ or ""
        _callback.__name__ = resource_view.__name__
        _callback.__module__ = resource_view.__module__
        
        _callback.__doc__ += u"""
            .. warning::
            
                Метод привязан к таблице %s! 
                
        """%self.table.__name__
        
        return _callback
            
            
    
    def get(self, self_resource):
        """
            Получает все объекты, соответствующие запросу query
        """
        with transaction.manager:
            db_data = sqlahelper.get_session().query(self.table)
            
            if self_resource.request.data["query"] != {}:
                db_data = QueryParser(self.table, 
                                      self.table._query(), 
                                      {"query": self_resource.request.data["query"]}).execute()
                
            return map(lambda x: x.__json__(self_resource.request), db_data.all())
        
    def post(self, self_resource):
        """
            Создает новый объект
        """
        with transaction.manager:
            try:
                db_item = self.table(**self_resource.request.data["body"])._add()._flush()
            except TypeError as x:
                raise BadRequest(info = str(x))
            
            return db_item.__json__(self_resource.request)
    
    def delete(self, self_resource):
        with transaction.manager:
            for id in self_resource.request.data["query"]:
                self.table._get(id = id)._delete()
        return "ok"
    
    def get_object(self, self_resource):
        with transaction.manager:
            db_item = self.table._get(id = self_resource.request.data["route"]["id"])
            return db_item.__json__(self_resource.request)
    
    def put_object(self, self_resource):
        with transaction.manager:
            db_item = self.table._get(id = self_resource.request.data["route"]["id"])
            
            for key, value in self_resource.request.data["body"].iteritems():
                try:
                    setattr(db_item, key, value)
                except:
                    raise BadRequest(info = "Incorrect field: %s"%key)
                
            return db_item.__json__(self_resource.request)
            
    def delete_object(self, self_resource):
        with transaction.manager:
            self.table._get(id = self_resource.request.data["route"]["id"])._delete()
            
        
        
            
        
        
            
    
    
        
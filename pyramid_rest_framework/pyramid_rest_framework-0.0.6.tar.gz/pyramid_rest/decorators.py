#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone
import os
from pyramid_rest.logger import Logger
from pprint import pformat, pprint
from jsonschema.validators import Draft3Validator, ErrorTree, Draft4Validator
from pyramid_rest.exceptions import ValidationError, UnknownError, BadRequest,\
    ExceptionInterface
import transaction
import sqlahelper
from bsddb import db
from jsonschema._format import FormatChecker
from pyramid_rest.querying import QueryParser
import traceback
from pyramid_rest.format_checker import OwnFormatChecker
from threading import Lock
import thread

class registerResource:
    """
        Регистрирует роуты для классов :class:`pyramid_rest.resources.Resource`. Пример использования::
        
            @registerResource("/users")
            class UserViews(Resource):
                ...
        
        Сам класс лишь сохраняет роуты в self.routes_meta, которые потом будут зарегестрированы в :class:`pyramid_rest.app.App` при помощи
        :func:`pyramid_rest.decorators.registerResource.register`
        
        При этом для каждого ресурса будут зарегестрированы 2 роута:
        
            * /users - табличный
            * /users/{id} - объектный.
        
        .. warning::
        
            Метод :func:`pyramid_rest.decorators.registerResource.register` должен быть вызван **после** того, как подгрузятся все ресурсы, декорированные этим декоратором.
            В противном случае, роуты зарегестрированы не будут.
        
        
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
        
        return resourceClass
    
    @staticmethod
    def register(app):
        """
            Выполняет регистрацию роутов в системе.
            
            :param app: :class:`pyramid_rest.app.App` инстанс
            
            .. warning::
            
                Этот метод должен вызываться **после** того, как загрузятся все определенные ресурсы. 
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
        
        :param function: Функция - валидатор. Принимает на вход экземпляр :class:`pyramid_rest.request.Request`. В случае ошибки валидации генерит инстанс :class:`pyramid_rest.exceptions.ValidationError` либо другую встроенную ошибку.
    
        .. note::
        
            В случае если у function задан параметр **__autodoc__**, строка документации заданная в этом параметре допишется
            к документации валидируемого метода.
    """ 
    def __init__(self, function):
        self.function = function
    
    def __call__(self, resource_view):
        def _callback(self_resource, request):
            try:
                self.function(request)
            except ExceptionInterface as x:
                raise x
            return resource_view(self_resource, request)
        _callback.__doc__ = resource_view.__doc__ or ""
        
        if hasattr(self.function, "__autodoc__"):
            _callback.__doc__ += u"""

* **Добавлен custom validator %s**. Подробнее:
    
    .. note::
    
        %s

"""%(self.function, getattr(self.function, "__autodoc__"))
        
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
        
            В целях безопасности, поля которые не указаны в body.schema, вырезаются из запроса, а в query.schema; body.schema добавляется параметр
            additionalProperties = False
        
        * В случае ошибки валидации генерится сообщение в формате::
        
            {
                "info": 
                    {
                        "body":         #ошибки в валидации body
                            {
                                "key2": "u'0' is not one of ['1', '2']"    #сообщение об ошибке
                                "key1": "u'1' is not of type 'integer'"
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
            #schema["body"]["additionalProperties"] = False
            self.bodySchema = schema["body"]
        else: self.bodySchema = None
        
        if "route" in schema: 
            schema["route"]["additionalProperties"] = False
            self.routeSchema = schema["route"]
        else: self.routeSchema = None
        
        self.cls = cls
    
    def _validateSchema(self, schema, data):
        
        if schema["type"] == "object":
            for key in data.keys():
                if key not in schema["properties"]:
                    del data[key]
        
        Logger().decorators.info("Changed request to %s", pformat(data))
        
        validator = Draft3Validator(schema, format_checker = OwnFormatChecker())
        
        Logger().decorators.info("Validating data %s with schema %s", pformat(data), pformat(schema))
        
        errors = {}
        
        for error in validator.iter_errors(data):
            if len(error.path)>0:
                errors[list(error.path)[-1]] = error.message
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
        
            @customValidator(CustomValidators.SomeValidator(some_arg))
            def get(self):
                ...
                
        Каждый валидатор является либо классом, с определенным методом **__call__**, либо функцией.
        При валидации, принимает объект текущего запроса :class:`partners_rest.request.Request`
    """
    
    class UserId:
        """
            Выполняет валидацию поля user_id текущей модели
            
            :param model: ORM модель, элемент которой должен быть провалидирован на владение текущим юзером
            
            Удобно использовать, вместе с **column_property**, которое возвращает id юзера - владельца объекта в БД
            Подробнее о **column_property**: http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html#using-column-property
        """
        def __init__(self, model):
            self.model = model
            
            
        def onget(self, request):
            """
                Выбирает из множества элементов привязанной таблицы
                только элементы, с user_id = userid текущего юзера
                
                Пример::
                    
                    @AllowToGroups("all")
                    @customValidator(UserId(Checkboxes).onget)
                    @bindTable(Checkboxes)
                    def get(self, data):pass
                
                вернет все чекбоксы текущего юзера
            """
            request.data["query"]["user_id"] = request.userid
            
        def onpost(self, request):
            """
                Устанавливает параметр user_id тела запроса в заданное значение id текущего юзера
                
                Пример:
                
                    @AllowToGroups("all"
                    @customValidator(UserId(Checkboxes).)
                    @bindTable(Checkboxes)
                    def get(self, data):pass
            """
            request.data["body"]["user_id"] = request.userid
        
        def owner(self, request):
            """
                .. warning::
                
                    Применим только для объектных роутов!
                    
                Проверяет, что текущий объект принадлежит текущему юзеру.
                У объекта должно быть определено свойство user_id - id юзера - владельца
            """
            with transaction.manager:
                db_object = self.model._get(id = request.data["route"]["id"])
                if db_object.user_id != request.userid:
                    raise ValidationError(info = {"route": {"id": "Incorrect parameter"}})
        
        def ondelete(self, request):
            """
                см. :func:`pyramid_rest.decorators.CustomValidators.UserId.owner`
            """
            self.owner(request)
        
        def onput(self, request):
            """
                см. :func:`pyramid_rest.decorators.CustomValidators.UserId.owner`
            """
            self.ondelete(request)
            
    
    class Exec:
        """
            Декоратор произвольного изменения.
            
            Пример::
            
                @customValidator(Exec("request.query['user_id'] = request.userid"))
                ...
                
            Принимает на вход **exec** интерпретируемую строку и выполняет ее. 
            Доступный контекст:
            
                * **request** - текущий запрос
            
        """
        def __init__(self, what):
            self.what = what
            self.__autodoc__ = u"""
        
        Добавлен декоратор произвольного изменения запроса. Декоратор проводит след. изменение::
        
            %s
        
            """%self.what
        
        def __call__(self, request):
            with transaction.manager:
                exec self.what
    
    class Assert:
        """
            Похож на декоратор :class:`pyramid_rest.decorators.CustomValidators.Exec`, за тем исключением, что проверяет что передаваемое выражение == True.
            Иначе, генерит **ValidationError**
        """
        def __init__(self, what):
            self.what = what
            self.__autodoc__ = u"""
        
        Добавлен декоратор произвольной валидации запроса. Декоратор проводит след. валидацию::
        
            %s
        
            """%self.what
        def __call__(self, request):
            with transaction.manager:
                if not eval(self.what):
                    raise ValidationError(info = "Assertion fails. Bad request")

    class AllowLikeFields:
        """
            Разрешает для переданных полей **fields** LIKE - запрос. 
            
            По умолчанию, LIKE запросы запрещены в целях безопасности. Если необходимо разрешить некоторому GET методу LIKE запрос то надо использовать этот декоратор::
            
                @customValidator(AllowLikeFields("label", "value"))
                @bindTable(Tickets)
                def get(self, data): pass
                
            .. note::
            
                Имеет смысл только для методов, покрытых декоратором :class:`pyramid_rest.decorators.bindTable`
                
            Подробнее о форматах запросов: :class:`pyramid_rest.querying.QueryParser`
                
        """
        def __init__(self, *fields):
            self.fields = fields
            self.__autodoc__ = u"""
            
        Разрешает для LIKE запросов следующие поля::
        
            %s
        
            """%self.fields
            
        def __call__(self, request):
            request.allowLikeFields += self.fields
    
    class ObjectOwner:
        """
            Декоратор, проводит валидацию *_object запроса
            
            :param table: ORM table object
            :param query: ORM query объект eval string 
            
            Пример::
            
                @customValidator(CustomValidators.ObjectOwner(User, "self.table.id == request.userid"))
        """
        def __init__(self, table, query):
            self.table = table
            self.query = query
            self.__autodoc__ = u"""
            
        Добавлен декоратор "владения объектом". Проверяется, что запрашиваемый объект:
        
            * Из таблицы %s
            * Удовлетворяет условию::
            
                %s
        
            """%(self.table, 
                 self.query)
            
        def __call__(self, request):
            query = eval(self.query)
            if self.table._filter(query).filter_by(id = int(request.data["route"]["id"])).first() is None:
                raise ValidationError(info = {"route": {"id": "Incorrect parameter"}})
    
    class UniqueField:
        """Декоратор, проверяет уникальность поля field в таблице Table.
        
            Пример::
            
                >>> @UniqueField(Users, 'email')
                
            :param table: ORM класс таблицы
            :param field: имя поля в body - запросе
            :param query: если передан этот параметр, и найденные объекты удовлетворяют этому запросу, то валидация проходится 
        """
        
        def __init__(self, table, field, query = None):
            self.table = table
            self.field = field
            self.query = query
            self.__autodoc__ = u"""
        Проверяет уникальность поля %s в таблице %s
            """%(self.field, self.table.__name__)
            
        def __call__(self, request):
                
            with transaction.manager:
                data = request.data["body"].get(self.field, None)
                db_items = self.table._filter_by(**{self.field: data})
                
                if db_items.count()>1:
                    raise ValidationError(info = {"body": {self.field: "Not unique value(many rows)"}})
                
                db_item = db_items.first()
                id = int(request.data["route"].get("id", 0))
                
                if not db_item is None:
                    if id != db_item.id:
                        raise ValidationError(info = {"body": {self.field: "Not unique value(incorrect id)"}})    
                
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
            self.__autodoc__ = u"""
            
        Из запроса будут удалены след. поля::
        
            %s
            
            """%self.fields
            
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
            self.__autodoc__ = u"""
            
        В запросе останутся только след. поля::
        
            %s
            
            """%self.fields
            
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
            
                @ForeignKey("ref_owner_id", Users, Users.id, {"user_id": 1})
                def post(...)
                
            В примере, значение поля "ref_owner_id" должно быть одним из id Юзеров у которых параметр "ref_is_manager" = 1
            
        """
        def __init__(self, field, table, column, query = {}, notnull = False, data_type = "body"):
            
            self.field = field
            self.table = table
            self.column = column
            self.query = query
            self.notnull = notnull
            self.data_type = data_type
            
            self.__autodoc__ = u"""
        Валидация типа "Внешний ключ". Проверяется поле %s. Родительская таблица ключа - %s(%s). 
        Дополнительный запрос на данные для внешнего ключа::
        
            %s
            
        Notnull: %s 
            """%(field, table, column, query, notnull)
            
        def __call__(self, request):
            field_data = request.data[self.data_type].get(self.field, None)
            
            with transaction.manager:
                if field_data is None:
                    if self.notnull:
                        raise ValidationError(info = {"body": {self.field: "Null values not allowed!"}})
                    else:
                        return
                
                Logger().decorators.info("Validating foreign key constraint. Params: %s", 
                                         pformat(locals()))
                
                db_item = self.table._filter(getattr(self.table, self.column) == field_data)

                for key, value in self.query.iteritems():
                    value = eval(value)
                    db_item = db_item.filter(getattr(self.table, key) == value)
                
                if db_item.first() is None:
                    raise ValidationError(info = {"body": {self.field: "Incorrect foreign key value."}})

class ApplyQuery:
    """
        Позволяет использовать все ништяки :class:`pyramid_rest.querying.QueryParser` даже если метод не прибинден к таблице с помощью
        :class:`pyramid_rest.decorators.bindTable`
        
        .. note::
        
            Декорируемый метод принимает request, и обязан возвращать sqlalchemy subquery object.
            Пример::
            
                @ApplyQuery()
                def get(self, request):
                    query = sqlahelper.get_session()\
                        .query(User.id.label("user_id"), 
                               User.nickname.label("nickname"), 
                               func.sum(WebmasterReferalPayment.amount).label("amount"), 
                               func.date(WebmasterReferalPayment.created).label("date"))\
                        .join(CommonReferalPayment, CommonReferalPayment.id == WebmasterReferalPayment.id)\
                        .join(User, CommonReferalPayment.child_id == User.id)\
                        .filter(WebmasterReferalPayment.user_id == request.userid)\
                        .group_by("user_id", "date")\
                        .subquery()
                    return query
                    
            При таком запросе, в request.data["query"] могут использоваться след. поля:
            
                * user_id
                * nickname
                * amount
                * date
            
    """
    def __init__(self): pass
    
    def __call__(self, view):
        def _c(self_resource, request):
            subquery = view(self_resource, request)
            
            query = QueryParser(subquery, 
                        sqlahelper.get_session().query(subquery),
                        request.data, 
                        request)
            
            with transaction.manager:
                out = query.execute().all()
                request.count = query.count
                
            return out
        
        _c.__doc__ = view.__doc__ or u""
        
        _c.__doc__ += u"""
        
.. note::

    Добавлен декоратор ApplyQuery. Это значит, можно использовать возможности QueryParser. 
    **Доступные для передачи в QueryParser поля доступны в описании маппинга. Если такового нет, значит произошла серьезная ошибка!**
        
        """
        
        _c.__name__ = view.__name__
        _c.__module__ = view.__module__
        
        return _c

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
        def _callback(self_request, request):
            data = resource_view(self_request, request)
            
            with transaction.manager:
                #try:
                if type(data) is list:
                    return map(lambda x: self.mapper(request, x), data)
                elif type(data) is dict:
                    return self.mapper(request, data)
                else:
                    Logger().decorators.warning("Incorrect value passed to mapper: %s", pformat(locals()))
                #except Exception as x:
                #    Logger().decorators.error("Error while mapping: %s\nLocals: %s", x, pformat(locals()))
                #    return data
        
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
        
        .. note::
        
            Этот декоратор по сути является "Ядром" проекта. Этот декоратор позволяет:
            
                * Использовать парсер запросов
                * не писать дублирующийся код
                
            По сути, декоратор производит следующее маппирование запросов:
            
                * GET запрос - получение элементов из таблицы
                * POST запрос - добавление нового элемента
                * PUT запрос - изменение элемента
                * DELETE запрос - удаление
                
            .. warning::
            
                POST и PUT запросы должны тщательно валидироваться.
                Все запросы должны проверяться на соответствие объект - владелец.
            
    """
    def __init__(self, sqlalchemy_table):
        self.type = type
        self.table = sqlalchemy_table
        
    def __call__(self, resource_view):
        def _callback(self_resource, request):
            
            if not hasattr(self, resource_view.__name__):
                raise UnknownError(info = "No views with name %s"%resource_view.__name__)
            
            request.bindedTable = self.table
            
            bind_output_data = getattr(self, resource_view.__name__)(request)
            resource_output_data = resource_view(self_resource, request, bind_output_data)
            
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
            
            
    
    def get(self, request):
        """
            Получает все объекты, соответствующие запросу query
        """
        
        with transaction.manager:
            db_data = sqlahelper.get_session().query(self.table)

            
            query = QueryParser(self.table, 
                                self.table._query(), 
                                request.data, 
                                request = request)
            
            db_data = query.execute()
            
            request.count = query.count
            request.query = request.data
                
            return map(lambda x: x.__json__(request), db_data.all())
        
    def post(self, request):
        """
            Создает новый объект
        """
        with transaction.manager:
            try:
                db_item = self.table(**request.data["body"])._add()._flush()
            except TypeError as x:
                raise BadRequest(info = str(x))
            
            return db_item.__json__(request)
    
    def delete(self, request):
        with transaction.manager:
            for id in request.data["query"]:
                self.table._get(id = id)._delete()
        return {"id": request.data["query"]}
    
    def get_object(self, request):
        with transaction.manager:
            db_item = self.table._get(id = request.data["route"]["id"])
            return db_item.__json__(request)
    
    def put_object(self, request):
        with transaction.manager:
            db_item = self.table._get(id = request.data["route"]["id"])
            
            for key, value in request.data["body"].iteritems():
                try:
                    setattr(db_item, key, value)
                except:
                    raise BadRequest(info = "Incorrect field: %s"%key)
                
            return db_item.__json__(request)
            
    def delete_object(self, request):
        with transaction.manager:
            self.table._get(id = request.data["route"]["id"])._delete()
            return {"id": request.data["route"]["id"]}
            
        
        
            
        
        
            
    
    
        
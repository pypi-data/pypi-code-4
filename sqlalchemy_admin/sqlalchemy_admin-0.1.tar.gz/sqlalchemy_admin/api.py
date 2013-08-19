#-*- coding: utf-8 -*-
from pyramid.exceptions import NotFound
from pyramid.response import Response
from crud import constructSuperModel
import wtforms
from views import api_index
import transaction
import json
import pyramid
items = {}

def singleton(clas, instances = {}):
    """Шаблон singleton - применяется к класу Api"""
    orig_init = clas.__init__
    def init(self, *a, **k):
        if clas.__name__ not in instances:
            orig_init(self, *a, **k)
            instances[clas.__name__] = self
        self.__dict__ = instances[clas.__name__].__dict__
    
    setattr(clas, "__init__", init)
    return clas    



class View:
    """Родительский класс всех представлений, отдающих JSON. Работает следующим образом::
    
            class MyViews(View):
                def view1(self):
                    return ["olala"]
                def view_help(self):
                    pass      
        
        В main::
    
            config.add_route("my route", "/my_lovely_prefix/{olala}", view = MyViews(what = "olala"), renderer = "json")
        
        В результате этих действий путь /my_lovely_prefix/view1 будет обслуживаться функцией view1, а путь 
        /my_lovely_prefix/view_help будет обслуживаться функцией view_help.
        
        Переменная request доступна как атрибут self.request.
        """
        
    def __init__(self, what = "action"):
        self.what = what
    
    def __call__(self, request):
        self.request = request
        self.action = self.request.matchdict[self.what]
        self.request.response.headers.update({"Content-type": "application/json; charset=utf-8"})
        
        
        if len(self.request.GET.keys())>0:
            self.data = self.request.GET
        elif len(self.request.POST.keys())>=0:
            self.data = self.request.POST
        
        if self.action[0]!="_":
            if hasattr(self, self.action):
                if hasattr(getattr(self, self.action), "__call__"):
                    return getattr(self, self.action)()
        return NotFound()

def json_map(request, arr):
    return map(lambda x: x.__json__(request), arr)

class TableApi(View):
    """Обслуживает основные CRUD запросы к одной таблице. Обслуживает роуты типа::
    
            /admin/<url_prefix>_<clas_name>/<action>
        
        :param url_prefix: - некоторый префикс. По умолчанию - api
        :param clas_name: - имя класса модели в нижнем регистре
        :param action: - действие. Для каждого action запрашиваемый роут обрабатывается функцией с именем <action>. См. :class:`View`
        
        Пример::
        
            /admin/api_users/add
        
        Этот путь будет обслуживаться функцией :func:`TableApi.add`
        
    """
    def __init__(self, clas, url_prefix = "api", api_method = "GET"):
        self.name = clas.__name__.lower()
        self.url = url_prefix+"_"+self.name
        self.api_method = api_method
        self.tablename = clas.__tablename__
        View.__init__(self, self.url)
        
        if not hasattr(clas, "_is_futured"):
            clas = constructSuperModel(clas)
            
        self.table = clas
        self._form = self.__form_constructor()
    
    def get_columns(self):
        """
            Возвращает список колонок таблицы. 
            Каждая колонка есть сериализованный особым образом класс :class:`column`.
        """
        def _prepare_columns(col):
            if "foreign_key" in col.flags:
                fk_table_class = Api().get_table_class_by_tablename(col.metadata["fk_table"])
                if fk_table_class is None:
                    raise ValueError("Внешний ключ таблицы %s - %s ссылается на таблицу %s, которая не зарегестрирована в API"%(self.name, col.name, col.metadata["fk_table"]))
                col.metadata["select"] = map(lambda x: {"id": x.id, col.name: unicode(x.__unicode__())}, fk_table_class.table._all())
                col.metadata["tablename"] = fk_table_class.name
            return col
        return json_map(self.request, map(_prepare_columns, self.table._columns))
    
    def get_data(self):
        """Отдает данные из таблицы, отфильтрованные по полученным параметрам {key: value}
        
                :param url: /admin/api_<name>/get_data
                :param type: GET
                :param data: {key1: value1, key2: value2, ...}
        """
        data = getattr(self.request, self.api_method)
        if len(data) == 0:
            data = self.table._all()
            return data
        return self.table._get(**data)
    
    def add(self):
        """Получает данные. ВСЕГДА используется POST. Добавляет в базу новый объект, согласно полученным данным
        
            :param url: /admin/api_<name>/add
            :param type: POST
            :param data: {field1: value1, field2: value2,...}
            
            .. warning::
            
                Имена полей формы должны совпадать с именами колонок класса таблицы БД.
        """
        if self.request.POST:
            form = self.__form_constructor()(self.request.POST)
            with transaction.manager:
                if form.validate():
                    self.table(**form.data)._add()._flush()
                    return {"success": "true"}
                else: return {"success": "false", "errors": form.errors, "msg": "validation error"}
        else:
            return {"success": "false", "msg": "no post data"}
        
    def update(self):
        """Изменяет объект с id равным переданному, согласно переданным значениям.
        
            Все параметры аналогичны :func:`TableApi.add`
        """
        if self.request.POST:
            form = self.__form_constructor()(self.request.POST)
            with transaction.manager:
                if form.validate():
                    data = {key:value for key, value in form.data.iteritems() if key[0] != "_" and \
                            value not in ("", )}
                    print data
                    self.table._get(id = self.request.POST["id"])._update(**data)
                    return {"response": "ok"}
                
    def set_boolean_many(self):
        ids, type, column_name = (json.loads(self.request.POST["ids"]), self.request.POST["type"], self.request.POST["column_name"])
        
        if type == "true":
            type = True
        else:
            type = False
        
        with transaction.manager:
            for id in json.loads(self.request.POST["ids"]):
                self.table._get(id=id)._update(**{column_name:type})
        return {"response": "ok"}
    
    def delete(self):
        """Получает массив id, удаляет все записи с такими id
            
            :param url: /admin/api_<name>/delete
            :param type: POST
            :param data: {json: [id1, id2,...]}
             
        """
        ids = json.loads(self.request.POST["json"])["ids"]
        with transaction.manager:
            for id in ids:
                self.table._get(id = id)._delete()
                transaction.commit()
            return {"response": "ok"}
        return {"response": "error"}
    
    def __form_constructor(self, validate_functions = []):
        class form(wtforms.Form):
            pass
        
        for column in self.table._columns:
            if not "noneditable" in column.flags:
                if column.type == "string":
                    setattr(form, column.name, wtforms.TextAreaField())
                elif column.type == "date":
                    setattr(form, column.name, wtforms.DateField())
                elif column.type == "datetime":
                    setattr(form, column.name, wtforms.DateTimeField())
                elif column.type == "boolean":
                    setattr(form, column.name, wtforms.BooleanField())
                else:
                    setattr(form, column.name, wtforms.StringField())
                
        for function in validate_functions:
            setattr(form, function.__name__, function)
        
        return form   
        
        
    def _includeme(self, config):
        config.add_route(self.url, "/admin/"+self.url+"/"+"{%s}"%(self.what), view = self, renderer = "json")
        
        

@singleton    
class Api(object):
    """Основной класс api. Singleton. Используется для регистрации моделей, внутри интерфейса. Пример::
    
            @Api()
            class MyModel(Base):
                __tablename__ = "my_simple_model"
                id = Column(Integer, primary_key = True)
            
        Или::
        
            MyMorePerfectModel = Api()(MyModel)
            
    """
    watcher_classes = {}
    
    
    def __call__(self, clas):
        table_api = TableApi(clas)
        self.watcher_classes[table_api.name] = table_api
        return constructSuperModel(clas)
    
    def get_table_class_by_tablename(self, tblname):
        """Возвращает зарегестрированный экземпляр класса :class:`TableApi` по названию таблицы.
        
            :param tblname: string, название таблицы
        """
        for table in self.watcher_classes.itervalues():
            if table.tablename == tblname or table.name == tblname.lower():
                return table
    
    def get_watcher_classes(self, request):
        """Возвращает названия всех таблиц, за которыми следит."""
        return {"keys": self.watcher_classes.keys()}
        
    def includeme(self, config):
        """Используется для регистрации API в системе. В файле __init__.py проекта::
        
                Api().includeme(config)
        """
        config.add_jinja2_search_path("partners.sqlalchemy_admin:templates")
        for clas in self.watcher_classes.itervalues():
            clas._includeme(config)
        config.add_route("api_index", "/admin/", view = api_index, renderer = "api_index.jinja2")
        config.add_static_view("api_static", "sqlalchemy_admin/static")
        config.add_route("api_get_table_names", "/admin/api/ajax/get_tables", self.get_watcher_classes, renderer = "json")
        


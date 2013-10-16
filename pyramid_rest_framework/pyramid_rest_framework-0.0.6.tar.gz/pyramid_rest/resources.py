#-*- coding: utf-8 -*-
from pyramid_rest.request import Request
from pyramid_rest.exceptions import MethodNotAllowed

class Resource:
    """
        От этого класса должны наследоваться все ресурсы. Пример использования данного класса::
        
            @routeRegister("/users")        #привязка класса к роуту
            class UserView(Resource):
            
                def get(self, request):
                    "Реализует get интерфейс для /users"
                def post(self, request):
                    "Реализует post интерфейс для /users"
                
                def delete(self, request):
                    "реализует delete для /users"
                
                def get_object(self, request):
                    "реализует get для /users/{id}"
                
                def put_object(self, request):
                    "реализует post для /users/{id}"
                
                def delete_object(self, request):
                    "реализует delete для /users/{id}
        
        .. warning::
        
            Метод PUT для табличного и POST для объектного роутов **запрещены**!
            
        .. note::
        
            * Каждый метод принимает объект :class:`pyramid_rest.request.Request`
                
            * Методы с суффиксом object обрабатывают объектные роуты
            
        :param app: текущий экземпляр :class:`pyramid_rest.app.App`
        
    """
    def __init__(self, app):
        self.app = app
        self.app.logger.resources.info("Initializing resource %s", self)
    
    def get_table_view(self):
        """
            Возвращает callback для обработки текущего запроса согласно методу запроса для табличного роута.
        """
        def _table_view(request):
            self.app.logger.resources.info("Called resource %s", self)
            
            method = request.get_method()
            
            if method not in ("get", "post", "delete"):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            if not hasattr(self, method):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            return getattr(self, method)(request)
        return _table_view
    
    def get_object_view(self):
        """
            Возвращает callback для обработки текущего запроса согласно методу запроса для табличного роута.
        """
        def _table_view(request):
            
            self.app.logger.resources.info("Called resource %s", self)
            
            method = request.get_method()
            
            if method not in ("get", "put", "delete"):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            view_name = method + "_object"
            
            if not hasattr(self, view_name):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            return getattr(self, view_name)(request)
        return _table_view
    
    
        
        
        
        
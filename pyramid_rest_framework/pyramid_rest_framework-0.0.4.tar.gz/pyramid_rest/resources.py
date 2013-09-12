#-*- coding: utf-8 -*-
from pyramid_rest.request import Request
from pyramid_rest.exceptions import MethodNotAllowed

class Resource:
    """
        От этого класса должны наследоваться все ресурсы. Пример использования данного класса::
        
            @routeRegister("/users")        #привязка класса к роуту
            class UserView(Resource):
            
                def get(self):
                    "Реализует get интерфейс для /users"
                def post(self):
                    "Реализует post интерфейс для /users"
                
                def delete(self):
                    "реализует delete для /users"
                
                def get_object(self):
                    "реализует get для /users/{id}"
                
                def put_obj(self):
                    "реализует post для /users/{id}"
                
                def delete_obj(self):
                    "реализует delete для /users/{id}
        
        .. warning::
        
            Метод PUT для табличного и POST для объектного роутов **запрещены**!
        
    """
    def __init__(self, app):
        self.app = app
        self.app.logger.resources.info("Initializing resource %s", self)
    
    def get_table_view(self):
        """
            Возвращает метод для обработки табличных роутов.
            Этот метод из обычного pyramid request создает экземпляр класса
            :class:`python_rest.request.Request`. Этот экземпляр созхраняется как self.request. Оригинальный pyramid request 
            сохраняется в self.pyramid_request. Далее пробуем из методов класса выбрать метод, который совпадает с названием
            HTTP метода запроса. Если не получается, генерим :class:`pyramid_rest.exceptions.MethodNotAllowed`, иначе возвращаем
            массив объектов
        """
        def _table_view(request):
            self.request = request
            self.pyramid_request = request.request
            
            self.app.logger.resources.info("Called resource %s", self)
            
            method = self.request.get_method()
            
            if method not in ("get", "post", "delete"):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            if not hasattr(self, method):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            return getattr(self, method)()
        return _table_view
    
    def get_object_view(self):
        """
            Возвращает метод для обработки объектных роутов.
            Этот метод из обычного pyramid request создает экземпляр класса
            :class:`python_rest.request.Request`. Этот экземпляр созхраняется как self.request. Оригинальный pyramid request 
            сохраняется в self.pyramid_request. Далее пробуем из методов класса выбрать метод, который совпадает с названием
            HTTP метода запроса. Если не получается, генерим :class:`pyramid_rest.exceptions.MethodNotAllowed`, иначе возвращаем
            массив объектов
        """
        def _table_view(request):
            self.request = request
            self.pyramid_request = request.request
            
            self.app.logger.resources.info("Called resource %s", self)
            
            method = self.request.get_method()
            
            if method not in ("get", "put", "delete"):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            view_name = method + "_object"
            
            if not hasattr(self, view_name):
                raise MethodNotAllowed(info = "Method %s not allowed"%(method))
            
            return getattr(self, view_name)()
        return _table_view
    
    
        
        
        
        
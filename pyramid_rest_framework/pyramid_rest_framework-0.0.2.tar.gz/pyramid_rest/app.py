#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone
from pyramid_rest.server import Server
from pyramid_rest.decorators import registerResource
from pprint import pprint
from pyramid_rest.logger import Logger



@singletone
class App:
    """
        Основной класс приложения.
        
        :param config: Pyramid config 
        
        Атрибуты:
        
            * **self.config** - pyramid config object
            * **self.resources** - все зарегестрированные в системе ресурсы в формате::
            
                {
                    resourceClass.__name__: {
                        "class": <class object>,
                        "url": <resource table url>
                    }
                }
    """
    def __init__(self, config):
        self.config = config
        self.resources = {}
        
    def initialize(self):
        self.logger = Logger(self)
        pprint(self.logger.__dict__)
        self.logger.app.info("Logger initialized")
        self.server = Server(self)
        self.logger.app.info("Server initialized")
#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone
import logging


@singletone
class Logger:
    """
        Обертка над logging
    """
    ALLOWED_LOGGERS = ['main',
                       'exceptions',
                       'request',
                       'resources',
                       'helpers',
                       'server',
                       'app',
                       'decorators',
                       'view',
                       'files',
                       'models',
                       'events']
    def __init__(self, app = None):
        for name in self.ALLOWED_LOGGERS:
            setattr(self, name, logging.getLogger(name))
            
            
        
    
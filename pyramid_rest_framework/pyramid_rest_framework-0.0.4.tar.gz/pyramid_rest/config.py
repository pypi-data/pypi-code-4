#-*- coding: utf-8 -*-
from pyramid_rest.helpers import singletone

@singletone
class Config:
    def __init__(self):
        pass
    
    def includeme(self, settings):
        self.settings = settings
        
        for key, value in settings.iteritems():
            setattr(self, key, value)
    
    def __getitem__(self, key):
        return self.settings[key]
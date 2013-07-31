from tornado.util import import_object
from settings import settings

class AdminSite(object):

    AVAILABLE_COLLECTIONS = {}

    def register(self, cls):
        #print 'reging', cls
        self.AVAILABLE_COLLECTIONS[cls.__name__.lower()] = cls

    def autodiscover(self):        
        for app in settings.get('apps', []):
            try:
                __import__(app, None, None, ['admin']).admin
            except:

                print app, 'failed'

    def get_class_for_name(self, name):
        return self.AVAILABLE_COLLECTIONS[name]

    def get_collections(self):
        return self.AVAILABLE_COLLECTIONS

admin = AdminSite()

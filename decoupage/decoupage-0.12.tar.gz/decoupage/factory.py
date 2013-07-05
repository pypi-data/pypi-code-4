from web import Decoupage
from paste.httpexceptions import HTTPExceptionHandler

def namespace_conf(keystr, app_conf):
    keystr += '.'
    return dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])        


def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    app_conf = namespace_conf('decoupage', app_conf)
    app = Decoupage(**app_conf)
    return HTTPExceptionHandler(app)
    

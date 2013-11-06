#!/usr/bin/env
from wsgiref.simple_server import make_server
from controller import DAV10Controller, DAV10RequestHandler
from DAV.INI_Parse import Configuration
from DAVServer.fshandler import FilesystemHandler
from DAVServer.server import runserver
import logging
#stripped down WSGI controller
wsgi_app = DAV10Controller

from logging_conf import syslogHandler 
log = logging.getLogger('pywebdav')
log.addHandler(syslogHandler)
log.setLevel(logging.DEBUG)

def gethandler(handler_class, directory, host, port, configfile=None, verbose=True):
    """Prepare and return a DAV 1.0 request handler"""
    # setup the configuration obj (required)
    if configfile is not None:
        setattr(handler_class, '_config', Configuration(configfile))

    # dispatch directory and host to the filesystem handler
    # This handler is responsible from where to take the data
    setattr(handler_class, 'IFACE_CLASS', \
        FilesystemHandler(directory, 'http://%s:%s/' % (host, port), verbose))

    return handler_class

if __name__ == '__main__':
    directory = '/home/research'
    host = 'localhost'
    port = 8081
    dav10handler = gethandler(
        DAV10RequestHandler, directory, host, port,
        configfile='webdav.conf')
    #import pdb; pdb.set_trace()
    #s = make_server(host, port, wsgi_app, \
    #    handler_class=davhandler)
    s = runserver(
        verbose=True, 
        directory=directory, 
        host=host, 
        port=port,
        user='test', 
        password='test00', 
        handler=dav10handler
    )
    s.serve_forever()


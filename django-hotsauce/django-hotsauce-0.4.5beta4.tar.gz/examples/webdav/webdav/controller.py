from threading import local
from functools import wraps
from wsgiref.simple_server import WSGIRequestHandler

#### PyWebDAV imports
#import DAV
#import DAV.WebDAVServer
#DAV.WebDAVServer.DEBUG = True
####
# DAV server extention to implement DAV responses
# for published realms
from pywebdav.server.fileauth import DAVAuthHandler
####

####
# Front end controller script to integrate the DAV fileserver
# API 
from notmm.controllers.wsgi import WSGIController
from notmm.utils.wsgilib import HTTPRequest, HTTPResponse
####

#Local modules
#import settings
#import utils

# DAV10_CONFIG = getattr(settings, 'DAV10_CONFIG', {})
# Setup the filesystem-based provider :-)
# DAV10_IFACE_CLASS = settings.MOUNTPOINTS['test']['root']

class DAVRequestHandler(WSGIRequestHandler, DAVAuthHandler):
 
    def __init__(self):
        pass

    def handle(self):
        DavAuthHandler.handle(self)


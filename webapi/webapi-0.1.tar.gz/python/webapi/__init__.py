from __future__ import absolute_import
from webapi.decorators import method, package
from webapi.protojson import encode_message
from webapi.service import Service
from webapi.errors import APIError, ServiceError
from webapi.handler import RPCHandler
from webapi.client import Client
from webapi.directoryhandler import APIDirectory
from webapi.apidescription import APIDescription
from protorpc.message_types import VoidMessage


def api(classes, name, version, description=None):
    api = APIDescription()
    api.name = name
    api.version = version
    api.description = description
    
    for cls in classes:
        api.add_class(cls)
        
    return api

def jsonrpc_handler(api_information):
    return type('Handler', (RPCHandler,), {'api_information': api_information})

from __future__ import absolute_import
from protorpc.messages import Message
from webapi.service import Service
from protorpc.message_types import VoidMessage

def package(name):
    def class_wrapper(cls):
        assert issubclass(cls, Service), "class must be a webapi.Service subclass"
        cls.__package_information = PackageInformation()
        cls.__package_information.name = name
        cls.__package_information.methods = {}
        cls.__package_information.cls = name
        return cls
    return class_wrapper


def check_valid_message_class(message_class, error_message):
    #if not isinstance(message_class, NoneType):    
    if not isinstance(message_class, type) or not issubclass(message_class, Message) or message_class is Message:
        raise TypeError(error_message)

def method(request_message, response_message, name, upload=False, cache_control=None):
    # TODO: accept NoneType
    assert isinstance(name, basestring), "Name must be a string"
    
    check_valid_message_class(request_message, "Request message must be NoneType or Message class")
    check_valid_message_class(response_message, "Response message must be NoneType or Message class")
    
    
    def method_wrapper(method):
        method.__method_information = MethodInformation()
        method.__method_information.name = name
        method.__method_information.cache_control = cache_control
        method.__method_information.request_message = request_message
        method.__method_information.response_message = response_message
        method.__method_information.method_name = method.__name__
        method.__method_information.method = method 
        method.__method_information.accepts_upload = upload

        if issubclass(request_message, VoidMessage):
            method.__method_information.requires_request = False
        
        if issubclass(response_message, VoidMessage):
            method.__method_information.returns_response = False
        
        return method
    
    return method_wrapper

class PackageInformation(object):
    name = None


class MethodInformation(object):
    """
        Properties:
            name: The method name.
            request_message: The request message class.
            response_message: The response message class.
            accepts_upload: Whether the request accepts a second upload parameter.
            requires_request: Whether the method requests a request.
            returns_response: Whether the method requires a response.
            cache_control: Unused for now.
    """
    name = None
    request_message = None
    response_message = None
    accepts_upload = False
    requires_request = True
    returns_response = True
    cache_control = None

from __future__ import absolute_import
import json
import logging

import webapp2
from protorpc import message_types
from protorpc.messages import Message
from webapi.errors import APIError
from webapi.protojson import encode_message, decode_dictionary


class Upload(object):
    content_type = ''
    filename = ''
    file = None

    def __init__(self, file, filename=None, content_type=None):
        assert hasattr(file, 'read'), 'File should have a read interface'
        self.file = file
        self.content_type = None
        self.filename = None




"""
 The "kind" property is used as a signal to downstream clients about what the resource 
 represents.
  
 This can be useful for clients that don't use Discovery in order 
 to map a generic JSON object to a strongly-typed class in code.
 
"""


class RPCHandler(webapp2.RequestHandler):
    """
        Handles JSONRPC style requests.
        
        
        An rpc can be simply called with an http request in the following form::
        
            POST /rpc HTTP/1.1
            Content-Length: <>
            Content-Type: application/json
            <other headers>
            
            {
                'jsonrpc': '2.0',
                'method': 'example.objects.insert',
                'params':[...]
            }
        
        Methods accepting uploads are handled using by building a multipart body::
        
            POST /rpc HTTP/1.1
            Content-Length: <>
            Content-Type: multipart/related; boundary=--xxx
            <other headers>

            --xxx
            Content-Type: application/json
            {
                'jsonrpc': '2.0',
                'method': 'example.objects.insert',
                'params':[...]
            }
            
            --xxx
            Content-Type: <upload content type>
            
            <upload data>
            
        
        An rpc and its upload can be submitted as form data.
        
        The field "request" must contain the jsonrpc message.
         
        The field "upload" should contain a file body. This will be passed as the upload parameter::
        
            POST /rpc HTTP/1.1
            Content-Length: <>
            Content-Type: multipart/form-data; boundary=--xxx
            <other headers>
            
            --xxx
            Content-Disposition: form-data; name="request"
            {
                'jsonrpc': '2.0',
                'method': 'example.objects.insert',
                'params':[...]
            }
            --xxx
            Content-Disposition: form-data; name="upload"; filename='file.o'
            Content-Type: <file mime type>
        
        
    """

    upload = None

    VERSION = '2.0'
    
    def get(self):
        """
        """
        # TODO: handle  jsonrpc get requests
        # XXX: possible base64
        # http://example.com/rpc?method=<method id>&params=<encoded params>&id=1
        return self.error(404)

    def get_upload(self):
        return self.upload


    def post(self):
        ''' TODO: if the request is form data, then the request is in "request", and any upload is under upload
        '''

        # if multipart/form-data, handle formdata requests (with uploads)
        if 'multipart/form-data' in self.request.headers['content-type']:
            args = self.request.POST.get('request')
            if 'upload' in self.request.POST:
                upload = self.request.POST.get('upload')
                # TODO: sanitize filename
                # TODO: NS: this would be better as upload.fp but it doenst work in tests
                content_type = upload.headers['Content-Type']
                self.upload = Upload(upload.file, upload.filename, content_type=content_type)

        else:
            args = self.request.body

        try:
            response = self.handle_request(args)
            self.handle_response(response)
        except APIError, e:
            self.handle_error(e)


    def handle_request(self, body):
        try:
            data = json.loads(body)
        except ValueError, e:
            raise APIError(code=APIError.ERROR_INVALID_BODY, message="Invalid body.")

        if data.get('jsonrpc') != self.VERSION:
            raise APIError(code=APIError.ERROR_INVALID_VERSION, message="Invalid rpc version.")

        method = data.get('method', None)

        if 'method' is None:
            # TODO: pass request_id
            raise APIError(code=APIError.ERROR_NO_METHOD, message='No method name')

        params = data.get('params', [])

        method_info = self.api_information.get_method_information(method)

        if method_info is None:
            raise APIError(code=APIError.ERROR_NO_METHOD, message='Invalid method')

        service_class = method_info.service_class

        if not hasattr(service_class, method_info.method_name):
            raise APIError(code=APIError.ERROR_NO_METHOD, message='Invalid method')

        request = None

        # use the first param for the request message
        if len(params):
            request = params[0]


        # err if a request message is required but none given
        if method_info.requires_request and request is None:
            raise APIError(code=APIError.ERROR_INVALID_REQUEST, message="Request message required")


        # also err if a message ISNT required but a message is given
        if not method_info.requires_request and request is not None:
            raise APIError(code=APIError.ERROR_INVALID_REQUEST,
                           message="Does not accept request message.")


        # convert the request message, NoneTypes turn to VoidMessage
        if request is None:
            request_message = message_types.VoidMessage()
        else:
            if not isinstance(request, dict):
                raise APIError(code=APIError.ERROR_INVALID_REQUEST,
                           message="Invalid request: %s" % request)

            request_message = self.decode_request_message(method_info.request_message, request)

        try:
            service = service_class()

            # pass the request to the service for initialization
            service.initialize(self.request)

            method = getattr(service, method_info.method_name, None)

            if method_info.accepts_upload:
                response = method(request_message, self.get_upload())
            else:
                response = method(request_message)
        except APIError as e:
            raise
        except Exception as e:
            logging.exception(e)
            raise APIError(code=APIError.ERROR_UNKNOWN_EXCEPTION,
                           message="Unknown service exception.")

        if method_info.returns_response:

            if not isinstance(response, Message):
                raise APIError(code=APIError.ERROR_INVALID_RESPONSE,
                               message="Response is not a Message.")

            try:
                response.check_initialized()
            except Exception as e:
                raise APIError(code=APIError.ERROR_INVALID_RESPONSE,
                               message="Response not initialized properly.")

            if not isinstance(response, method_info.response_message):
                raise APIError(code=APIError.ERROR_INVALID_RESPONSE,
                               message="Invalid response message.")

        return response

    def decode_request_message(self, message_type, request):
        # decode the request dictionary as a message
        try:
            request_message = decode_dictionary(message_type, request)
            return request_message
        except Exception, e:
            logging.exception(e)
            raise APIError(code=APIError.ERROR_INVALID_REQUEST,
                           message="Invalid request message: " + str(e))

    def handle_response(self, response, request_id=None):
        self.response.write(self.encode_response(response, request_id))

    def handle_error(self, error, request_id=None):
        self.response.write(self.encode_error(error, request_id))


    def encode_response(self, response, request_id=None):
        res = {
            'result': response,
            'id': request_id,
            'jsonrpc': self.VERSION
        }
        return encode_message(res)


    def encode_error(self, error, request_id=None):
        res = {
            'error': error.message,
            'id': request_id,
            'jsonrpc': self.VERSION
        }

        return encode_message(res)


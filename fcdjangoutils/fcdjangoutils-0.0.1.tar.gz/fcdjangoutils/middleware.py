import fcdjangoutils.responseutils
import threading
import django.core.handlers.base  
import django.test.client  

class EarlyResponse(object):
    def process_exception(self, request, exception):
        if isinstance(exception, fcdjangoutils.responseutils.EarlyResponseException):
            return exception.get_response(request)

_requests = threading.local()

  
class RequestMock(django.test.client.RequestFactory):  
    def request(self, **request):  
        "Construct a generic request object."  
        request = django.test.client.RequestFactory.request(self, **request)  
        handler = django.core.handlers.base.BaseHandler()  
        handler.load_middleware()  
        for middleware_method in handler._request_middleware:  
            if middleware_method(request):  
                raise Exception("Couldn't create request mock object - "  
                                "request middleware returned a response")  
        return request 
request_mock = RequestMock()

def get_request():
    if not hasattr(_requests, 'request'):
        print "Using mock request as no real request was found"
        _requests.request = request_mock.request()
    return _requests.request

class GlobalRequestMiddleware(object):
    def process_request(self, request):
        _requests.request = request

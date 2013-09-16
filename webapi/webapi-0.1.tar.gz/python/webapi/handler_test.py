from __future__ import absolute_import
import webtest
import unittest
import json
import webapp2
import webapi
import logging
import protorpc.messages as messages
from webapi import APIError

class TestRequest(messages.Message):
    string = messages.StringField(1)

class TestResponse(messages.Message):
    string = messages.StringField(1)

@webapi.package('test')
class TestService(webapi.Service):
    
    @webapi.method(TestRequest, TestResponse, 'test')
    def test(self, request):
        """ an identity function"""
        assert isinstance(request, TestRequest)
        return TestResponse(string=request.string)
    
    @webapi.method(TestRequest, TestResponse, 'upload', upload=True)
    def upload(self, request, upload=None):
        """ an identity function"""
        assert isinstance(request, TestRequest)
            
        return TestResponse(string=upload.file.read())
    

def build_test_app(service):
    API = webapi.api([service], 'testapi', 'v1')
    routes = [
        webapp2.Route('/rpc', webapi.jsonrpc_handler(API))
    ]
    wsgi_app = webapp2.WSGIApplication(routes)
    return webtest.TestApp(wsgi_app)
    
def build_jsonrpc_request(method, request):
    message = {
        'jsonrpc': '2.0',
        'method': method,
        'params': [request],
        'id': 1
    }
    return webapi.encode_message(message)
    

    
class Test(unittest.TestCase):
    def test_api_info(self):
        ''' Test api info '''
        API = webapi.api([TestService], 'testapi', 'v1')
        self.assertEqual({'testapi.test.test', 'testapi.test.upload'}, set(API.method_map.keys()))
    
        
    def test_service(self):
        test_app = build_test_app(TestService)
        response = build_and_send(test_app, 'testapi.test.test', TestRequest(string='Test'))
        # test we got the identity back
        self.assertEqual('Test', response['result']['string'])


    def test_invalid_method(self):
        """ test invalid method name """
        test_app = build_test_app(TestService)
        response = build_and_send(test_app, 'testapi.test.invalid', TestRequest(string='Test'))
        # test we got the identity back
        self.assertEqual('Invalid method', response['error']['message'])
        
        
    
    def test_form_upload(self):
        app = build_test_app(TestService)
        
        request = TestRequest(string='Test')
        request = build_jsonrpc_request('testapi.test.upload', request)
        
        response = app.post('/rpc', {
            'request': request,
            'upload': webtest.Upload('test.txt', 'Upload test')
        })
        
        self.assertEqual('Upload test', json.loads(response.body)['result']['string'])
    
    
    def test_service_request_error(self):
        """ Test invalid requests
        """
        test_app = build_test_app(TestService)
        response = build_and_send(test_app, 'testapi.test.test', None)
        self.assertEqual(APIError.ERROR_INVALID_REQUEST, response['error']['code'])
        
    def test_service_exception(self):
        """ Test when exceptions is raised from the service. 
        """
        
        @webapi.package('test')
        class InvalidService(webapi.Service):
            
            @webapi.method(TestRequest, TestResponse, 'test')
            def test(self, request):
                """ an identity function"""
                raise Exception("Test")
                
        test_app = build_test_app(InvalidService)  
        response = build_and_send(test_app, 'testapi.test.test', TestRequest(string='Test'))
        
        self.assertEqual(APIError.ERROR_UNKNOWN_EXCEPTION, response['error']['code'])

    


class DirectoryTest(unittest.TestCase):
    def test_directory(self):
        
        api1 = webapi.api([TestService], 'testapi', 'v1')
        
        test_app = webtest.TestApp(webapi.APIDirectory([api1]))
        
        # TODO: assert the directory was generated properly
        print test_app.get('/discovery/v1/apis')
        
        # TODO: assert the api was generated properly
        print test_app.get('/discovery/v1/apis/testapi/v1/rest')
        
        #self.fail()


def build_and_send(app, method, request):
    request = build_jsonrpc_request(method, request)  
    response = app.post('/rpc', request, content_type='application/json')
    return json.loads(response.body)

if __name__ == '__main__':
    unittest.main()
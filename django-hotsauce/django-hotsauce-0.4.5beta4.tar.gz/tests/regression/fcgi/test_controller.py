import sys
#import mainapp

from notmm.controllers.auth import AuthCookieController
from notmm.utils.wsgilib import HTTPRequest

from test_support import (
    WSGIController,
    WSGIControllerTestCase, 
    TestClient, 
    unittest,
    make_app,
    settings
    )

class AuthkitControllerTestCase(WSGIControllerTestCase):

    wsgi_app = AuthCookieController
    auth_conf = {
        'authkit.setup.method': ('redirect','cookie'), #form
        'authkit.redirect.url': '/session_login/',
        'authkit.cookie.secret': '12345'}
    
    def setUp(self):
        self.callback = self.wsgi_app(WSGIController(),
            self.auth_conf, settings=settings) #self.wsgi_app()
        self.client = self.wsgi_client(self.callback)  
        #setup_test_handlers(self.callback, settings)
 
    def test_get_response(self):
        rsp = self.client.get('/')
        self.assertEqual(rsp.status_code, '200 OK')

    def test_session_login(self):
        response = self.client.get('/session_login/') # 
        self.assertEqual(response.status_code, '200 OK')

    def test_session_login_POST(self):
        # XXX authenticate_user method test
        postdata = {
            'username': 'guest',
            'password': 'guest'}
        
        client = TestClient(self.callback, method="POST")
        client.environ.update(postdata)
        
        req = HTTPRequest(environ=client.environ.copy())
        self.assertEqual(req.method, 'POST')
        
        response = self.client.post('/session_login/', request=req)
        
        self.assertEqual(response.status_code, '200 OK')
        self.assertEqual('REMOTE_USER' in response.environ, True)


import sys
#import mainapp
from notmm.controllers.auth import AuthCookieController
from notmm.utils.wsgilib import HTTPRequest

from test_support import (
    WSGIControllerTestCase,
    WSGIController,
    TestClient, 
    unittest,
    make_app,
    settings
    )

class AuthkitControllerTestCase(WSGIControllerTestCase):

    wsgi_app = WSGIController #AuthCookieController
    

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
        import pdb; pdb.set_trace()
        response = self.client.post('/session_login/', request=req)
        
        self.assertEqual(response.status_code, '200 OK')
        self.assertEqual('REMOTE_USER' in response.environ, True)


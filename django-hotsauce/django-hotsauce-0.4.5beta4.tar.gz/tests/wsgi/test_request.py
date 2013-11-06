import os, sys

from notmm.utils.configparse import is_string
from notmm.utils.django_compat import get_callable
from notmm.utils.wsgilib import HTTPRequest
from notmm.utils.markup import FormWrapper
from test_support import WSGIControllerTestCase

class HTTPRequestTestCase(WSGIControllerTestCase):

    def test_post_required(self):
        client = self.client
        req = HTTPRequest()
        req.environ['REQUEST_METHOD'] = 'POST'
        req.environ.update({'foo' : 'bar'})
        response = client.post('/', request=req)

    #request methods
    def test_environ_getter(self):
        
        self.assertEqual(hasattr(self.callback, 'environ'), True)
        env = self.callback.environ
        self.assertEqual(isinstance(env, dict), True)
    


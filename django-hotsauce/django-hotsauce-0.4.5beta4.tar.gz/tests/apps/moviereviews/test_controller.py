import sys
#import mainapp

from test_support import (
    WSGIControllerTestCase, 
    TestClient, 
    unittest,
    make_app,
    settings,
    ResponseClass
    )

class WSGIAppTestCase(WSGIControllerTestCase):

    def test_render_index(self):
        response = self.client.get('/') # 
        self.assertEqual(response.status_code, '200 OK')

    def test_post_required_with_schevo_db(self):
        response = self.client.post('/test_post_required_with_schevo_db', data={})
        #print response.__name__
        self.assertEqual(isinstance(response, ResponseClass), True, type(response))
        self.assertEqual(response.status_code, '200 OK')


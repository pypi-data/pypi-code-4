#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from notmm.controllers.schevo  import SchevoController
from notmm.utils.configparse   import loadconf
from notmm.utils.wsgilib       import HTTPRequest, HTTPResponse

from test_support import (
    BaseControllerTestCase, TestClient,
    settings,
    setup_test_handlers
    )

def get_app_conf(section):
    return loadconf('development.ini', section=section)

class SchevoControllerTestCase(BaseControllerTestCase):

    wsgi_app = SchevoController
    response_class = HTTPResponse

    def __init__(self, methodName='runTest'):

        super(BaseControllerTestCase, self).__init__(methodName)
        env = os.environ.copy()

        self.request = HTTPRequest(env)
        self.request_class = type(self.request)

    def setUp(self):
        self.callback = self.wsgi_app(
            #the HTTP request obj for testing
            self.request,
            settings.SCHEVO['DATABASE_NAME']
            )

        setup_test_handlers(self.callback, settings)
        self.client = TestClient(self.callback)

    def tearDown(self):
        self.callback = None

    def test_with_schevo_database(self):
        response = self.client.post('/test_post_required_with_schevo_db', request=self.request)
        self.assertEqual(response.status==403, True)



#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import os
#import traceback
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from notmm.controllers.wsgi             import BaseController, WSGIController
from notmm.utils.django_settings        import SettingsProxy
from notmm.utils.wsgilib                import HTTPRequest, HTTPResponse
from test_client                        import TestClient

from sandbox import global_conf as app_conf

settings = SettingsProxy(autoload=True).settings

ResponseClass = HTTPResponse
RequestClass = HTTPRequest

#import logging_conf, logging
#logger = logging.getLogger(__name__)

def make_app(callback, *args, **kwargs):
    return callback(*args, **kwargs)

def setup_test_handlers(callback, settings):
    #if settings.DEBUG:
    #    print('function %s registered to %s' % (func_name, module))
    callback.registerWSGIHandlers(settings.CUSTOM_ERROR_HANDLERS)
    return None

def inittestpackage():
    if 'settings' in sys.modules:
        del sys.modules['settings']

# default test controller
class BaseControllerTestCase(unittest.TestCase):
    wsgi_app = BaseController
    wsgi_client = TestClient
    
    def setUp(self):
        self.callback = self.wsgi_app() #self.wsgi_app()
        self.client = self.wsgi_client(self.callback)  
        #setup_test_handlers(self.callback, settings)
    
    def tearDown(self):
        self.callback = self.client = None
    
class WSGIControllerTestCase(BaseControllerTestCase):
    #
    # Core tests for the WSGIController extension
    #
    wsgi_app = WSGIController

    def __init__(self, methodName='runTest'):
        super(WSGIControllerTestCase, self).__init__(methodName)

        self.settingsClass = type(settings)
        self.callback = None

    def test_base(self):
        #self.assertEqual(self.callback.request_class != None, True)
        if self.callback is not None:
            self.assertEqual(self.callback.get_request() != None, True)
            self.assertEqual(
                isinstance(self.callback.request, RequestClass),
                True,
                type(self.callback.request)
            )

      #def test_custom_error_handlers(self):
    #    self.assertEqual(isinstance(self.settingsClass, SettingsProxy), True, self.settingsClass)


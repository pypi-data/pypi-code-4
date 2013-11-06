#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BCLO Controller API Test-Suite
import unittest

from notmm.controllers.elixir   import ElixirController
from notmm.utils.wsgilib        import HTTPRequest, HTTPResponse
from test_support               import BaseControllerTestCase, settings

class ElixirControllerTestCase(BaseControllerTestCase):
    
    wsgi_app = ElixirController

    def __init__(self, methodName='runTest'):
        super(ElixirControllerTestCase, self).__init__(methodName)
        self.callback = self.wsgi_app(engine_name='sqlite:///foo.db', settings=settings)

    def test_get_or_set_engine(self):
        self.failIfEqual(self.callback.engine, None)
    
    def test_init_session(self):
        self.failUnlessEqual(hasattr(self.callback, 'init_session'), True)


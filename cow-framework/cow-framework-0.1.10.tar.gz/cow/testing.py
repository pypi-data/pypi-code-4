#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.testing import AsyncHTTPTestCase


class CowTestCase(AsyncHTTPTestCase):
    def get_server(self):
        raise NotImplementedError('You must implement the get_server method in your CowTestCase')

    def setUp(self, *args, **kwargs):
        self.server = self.get_server()
        self.server.plugin_before_start()
        self.server.plugin_after_start()

        super(CowTestCase, self).setUp(*args, **kwargs)

    def get_app(self):
        return self.server.application

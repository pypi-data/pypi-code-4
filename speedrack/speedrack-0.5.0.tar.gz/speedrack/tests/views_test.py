from speedrack import app

from flask import url_for

from nose.tools import *

class TestRoutes(object):
    client = app.test_client()

    def check_route(self, expected, route):
        assert_equal(expected, url_for(route))

    def test_routes(self):
        tests = [
            ("/", "show_tasks"),
            ("/config/clear", "clear_config"),
            ("/config/reload", "reload_config"),
            ("/debug", "show_debug"),
            ("/toggle_inactive", "toggle_inactive_tasks"),
            ("/help", "show_help"),
        ]
        with app.test_request_context():
            for (expected, route) in tests:
                yield self.check_route, expected, route


from werkzeug.test import EnvironBuilder

import unittest

from restpy.wrappers import Request


class TestWrappers(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestWrappers, self).setUp()
        self.environ = EnvironBuilder(path="/", method="GET").get_environ()

    def test_can_wrap_environ(self):

        Request(self.environ)

    def test_adds_uuid(self):

        request = Request(self.environ)

        self.assertTrue(hasattr(request, "uuid"))

#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock, sentinel
from ilogue.readable import assertMethod, setupMethod

class FormInteractionTestCase(unittest.TestCase):


    def test_submit_performs_assertRequest_with_url_from_form(self):
        from ilogue.readable.FormInteraction import FormInteraction
        from ilogue.readable.AssertableRequest import AssertableRequest
        requestMock = Mock()
        inter = FormInteraction('<form action="mytesturl"></form>', requestMock)
        returned = inter.submit()
        (assertMethod(requestMock).wasCalled()
            .withArgument("mytesturl"))

    def test_submit_performs_assertRequest_with_method_from_form_or_post_default(self):
        from ilogue.readable.FormInteraction import FormInteraction
        from ilogue.readable.AssertableRequest import AssertableRequest
        requestMock = Mock()
        default = FormInteraction('<form action="u"/>', requestMock)
        returned = default.submit()
        (assertMethod(requestMock).wasCalled()
            .withArguments(method="POST"))
        requestMock = Mock()
        get = FormInteraction('<form action="u" method="GET" />', requestMock)
        returned = get.submit()
        (assertMethod(requestMock).wasCalled()
            .withArguments(method="GET"))


if __name__ == '__main__':
    unittest.main()

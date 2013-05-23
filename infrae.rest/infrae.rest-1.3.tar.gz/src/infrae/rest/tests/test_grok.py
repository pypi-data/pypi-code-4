# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import doctest

import infrae.rest
from infrae.wsgi.testing import ZopeBrowserLayer, suite_from_package, http


class RestLayer(ZopeBrowserLayer):
    default_users = {
        'manager': ['Manager'],
        }


layer = RestLayer(infrae.rest)
globs = {'http': http,
         'getRootFolder': layer.get_application,
         'grok': layer.grok,}


def create_test(build_test_suite, name):
    test = build_test_suite(
        name,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = layer
    return test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suite_from_package('infrae.rest.tests.grok', create_test))
    return suite

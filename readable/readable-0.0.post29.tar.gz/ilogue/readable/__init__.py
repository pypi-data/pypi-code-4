#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

def assertObject(val):
    from ilogue.readable.assertableobject import AssertableObject
    return AssertableObject(val)


def assertMethod(methodMock):
    from ilogue.readable.assertablemethod import AssertableMethod
    return AssertableMethod(methodMock)


def assertContext(contextProviderMock):
    from ilogue.readable.AssertableContext import AssertableContext
    return AssertableContext(contextProviderMock)


def setupMethod(methodMock):
    from ilogue.readable.configurablemethod import ConfigurableMethod
    return ConfigurableMethod(methodMock)


def assertResponse(response=None, content = None):
    from ilogue.readable.assertableresponse import AssertableResponse
    return AssertableResponse(response,content)


def assertionMethod(method):
    from ilogue.readable.assertableassertion import AssertableAssertion
    return AssertableAssertion(method)

def assertRequest(url, **kwargs):
    from ilogue.readable.AssertableRequest import AssertableRequest
    return AssertableRequest(url, **kwargs)

from ilogue.readable.FormMatcher import FormMatcher
from ilogue.readable.FormInteraction import FormInteraction
from ilogue.readable.MockImplementation import mockImplementation


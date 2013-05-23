# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.location.interfaces import ILocation
from zope.browser.interfaces import IBrowserView
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import Attribute, implements


class IRESTComponent(IBrowserPublisher, ILocation, IBrowserView):
    """A REST component
    """


class IRESTMethodPublishedEvent(IObjectEvent):
    """Event triggered when a method is published.
    """
    method = Attribute("Published method name")


class RESTMethodPublishedEvent(ObjectEvent):
    implements(IRESTMethodPublishedEvent)

    def __init__(self, object, method):
        super(RESTMethodPublishedEvent, self).__init__(object)
        self.method = method


class MethodNotAllowed(Exception):
    """This method is not allowed.
    """


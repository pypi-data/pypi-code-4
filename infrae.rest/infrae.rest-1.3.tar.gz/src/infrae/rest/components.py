# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getMultiAdapter, queryAdapter
from zope.event import notify
from zope.interface import Interface
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.namespace import view

from Products.Five import BrowserView
from zExceptions import NotFound

from infrae.rest.interfaces import RESTMethodPublishedEvent
from infrae.rest.interfaces import MethodNotAllowed, IRESTComponent
from zeam.component import Component, getComponent

import json

_marker = object()
ALLOWED_REST_METHODS = ('GET', 'POST', 'HEAD', 'PUT',)


def queryRESTComponent(specs, args, name=u'', parent=None, id=_marker):
    """Query the ZCA for a REST component.
    """
    factory = getComponent(specs, IRESTComponent, name, default=None)
    if factory is not None:
        result = factory(*args)
        if result is not None and IRESTComponent.providedBy(result):
            # Set parenting information / for security
            if id is _marker:
                id = name
            result.__name__ = id
            result.__parent__ = parent
            return result
    return None


def lookupREST(context, request, name):
    """Lookup a REST component called name on the given context / request.
    """
    view = queryRESTComponent(
        (Interface, context,),
        (context, request),
        name=name,
        parent=context)
    if view is None:
        raise NotFound(name)
    return view


class REST(Component):
    """A base REST component
    """
    grok.baseclass()
    grok.implements(IRESTComponent)
    grok.provides(IRESTComponent)
    grok.adapts(Interface, None)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def response(self):
        return self.request.response

    def browserDefault(self, request):
        """Render the component using a method called the same way
        that the HTTP method name.
        """
        if request.method in ALLOWED_REST_METHODS:
            if hasattr(self, request.method):
                return self, (request.method,)
        raise MethodNotAllowed(request.method)

    def publishTraverse(self, request, name):
        """You can traverse to a method called the same way that the
        HTTP method name, or a sub view
        """
        if name in ALLOWED_REST_METHODS and name == request.method:
            if hasattr(self, name):
                notify(RESTMethodPublishedEvent(self, name))
                return getattr(self, name)
        view = queryRESTComponent(
            (self, self.context),
            (self.context, request),
            name=name,
            parent=self)
        if view is None:
            raise NotFound(name)
        return view

    def json_response(self, result):
        """Encode a result as a JSON response.
        """
        self.response.setHeader('Content-Type', 'application/json')
        return json.dumps(result)


class RESTWithTemplate(REST):
    grok.baseclass()
    template = None

    def __init__(self, context, request):
        super(RESTWithTemplate, self).__init__(context, request)
        static_name = getattr(self, '__static_name__', None)
        if static_name is not None:
            self.static = queryAdapter(
                request, Interface, name=static_name)
            if self.static is not None:
                self.static.__parent__ = context
        else:
            self.static = None

    def default_namespace(self):
        return {'rest': self,
                'context': self.context,
                'request': self.request}

    def namespace(self):
        return {}


class MethodNotAllowedView(grok.View):
    grok.context(MethodNotAllowed)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(405)

    def render(self):
        return u"Method not allowed"


class RESTNamespace(view):
    """Implement a namespace ++rest++.
    """

    def traverse(self, name, ignored):
        if name:
            return lookupREST(self.context, self.request, name)
        return self.context


class AbsoluteURL(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._parent_url = getMultiAdapter(
            (context.__parent__, request), IAbsoluteURL)

    def __str__(self):
        pattern = '%s/++rest++%s'
        if IRESTComponent.providedBy(self.context.__parent__):
            pattern = '%s/%s'
        return pattern % (self._parent_url(), self.context.__name__)

    __call__ = __repr__ = __unicode__ = __str__

    def breadcrumbs(self):
        return self._parent_url.breadcrumbs()

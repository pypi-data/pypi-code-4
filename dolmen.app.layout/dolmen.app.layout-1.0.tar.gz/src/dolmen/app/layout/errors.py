# -*- coding: utf-8 -*-

import grokcore.view as grok
from dolmen.app.layout import Page
from zope.publisher.interfaces import INotFound
from zope.location import LocationProxy

grok.templatedir("templates")


class NotFound(Page):
    grok.name("index.html")
    grok.context(INotFound)
    grok.require("zope.Public")

    @apply
    def context():
        # This is done to avoid redefining context in the __init__, after
        # calling Page.__init__. This way, the error is directly located.

        def fset(self, error):
            self._context = LocationProxy(error, error.ob, "")

        def fget(self):
            return self._context

        return property(fget, fset)

    def update(self):
        self.request.response.setStatus(404)

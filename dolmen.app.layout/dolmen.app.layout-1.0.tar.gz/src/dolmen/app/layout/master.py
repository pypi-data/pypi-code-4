# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from grokcore.layout import Layout
from dolmen.app.layout import interfaces as API
from megrok.resourceviewlet import ResourcesManager
from zope.interface import Interface, moduleProvides
from zope.traversing.browser import absoluteURL
from zope.container.interfaces import IContainer

grok.templatedir('templates')


class Master(Layout):
    grok.name('master')
    grok.context(Interface)

    def update(self):
        self.base = absoluteURL(self.context, self.request)
        if IContainer.providedBy(self.context) and self.base[:-1] != '/':
            self.base = self.base + '/'


class Resources(ResourcesManager):
    grok.name('dolmen.resources')
    grok.context(Interface)


class Header(grok.ViewletManager):
    grok.name("dolmen.header")
    grok.context(Interface)


class Top(grok.ViewletManager):
    grok.name("dolmen.top")
    grok.context(Interface)


class Footer(grok.ViewletManager):
    grok.name("dolmen.footer")
    grok.context(Interface)


class AboveBody(grok.ViewletManager):
    grok.name("dolmen.above.body")
    grok.context(Interface)


class BelowBody(grok.ViewletManager):
    grok.name("dolmen.below.body")
    grok.context(Interface)


moduleProvides(API.IGlobalUI)
__all__ = list(API.IGlobalUI)

# -*- coding: utf-8 -*-

import grokcore.viewlet as grok

from zope.interface import moduleProvides
from zope.publisher.interfaces import browser

from dolmen.app.layout import interfaces as API
from dolmen.app.layout.master import Resources
from megrok.resourceviewlet import ResourceViewlet


class IBaseLayer(browser.IDefaultBrowserLayer):
    """Base layer for a dolmen application
    """


class IBaseSkin(IBaseLayer, browser.IBrowserSkinType):
    """A very basic skin, implementing the needed layers to have a fully
    functional display : forms and other components.
    """
    grok.skin("basic_dolmen_skin")


class Resource(ResourceViewlet):
    grok.baseclass()
    grok.viewletmanager(Resources)


moduleProvides(API.ISkin)
__all__ = list(API.ISkin)

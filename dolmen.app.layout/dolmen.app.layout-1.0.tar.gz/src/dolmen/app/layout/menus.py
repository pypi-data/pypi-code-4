# -*- coding: utf-8 -*-

import grokcore.viewlet as grok

from dolmen import menu
from dolmen.app.layout import interfaces as API
from zope.interface import moduleProvides, Interface


class ContextualMenu(menu.Menu):
    grok.context(Interface)
    grok.name('contextual-actions')
    grok.title(u'Contextual actions')


class MenuViewlet(grok.Viewlet):
    grok.baseclass()
    grok.require("dolmen.content.View")

    menu_class = u"menu"
    entry_class = u"entry"
    actions = []

    @property
    def menu_factory(self):
        raise NotImplementedError("You need to specify a menu class.")

    def get_context(self):
        return self.context

    def update(self):
        context = self.get_context()
        self.menu = self.menu_factory(context, self.request, self.view)
        self.menu.update()

    def render(self):
        return self.menu.render()


moduleProvides(API.IMenus)
__all__ = list(API.IMenus)

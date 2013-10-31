
# -*- coding: utf-8 -*-

import grok
from dolmen import menu

from dolmen.app.authentication import MF as _
from dolmen.app.layout import master, MenuViewlet
from dolmen.app.layout.viewlets import ContextualActions
from dolmen.app.security.content import CanViewContent
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.interface import Interface

grok.context(Interface)


class AnonymousActionsMenu(menu.Menu):
    grok.context(Interface)
    grok.name('anonymous-actions')
    grok.title(_(u'Public actions'))


class UserActionsMenu(menu.Menu):
    grok.context(Interface)
    grok.name(u'user-actions')
    grok.title(_(u'User actions'))


class ActionBarViewlet(ContextualActions):
    grok.order(20)
    grok.name('dolmen.actionbar')
    grok.require(CanViewContent)
    grok.viewletmanager(master.Top)

    @property
    def menu_factory(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return AnonymousActionsMenu
        return UserActionsMenu

    def update(self):
        MenuViewlet.update(self)
        self.actions = self.compute_actions(self.menu.viewlets)

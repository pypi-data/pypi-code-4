# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from dolmen.app.layout import ContextualMenu, MenuViewlet, AboveBody, Top
from dolmen.app.layout import interfaces as API
from grokcore.message import receive
from zope.interface import Interface, moduleProvides


class FlashMessages(grok.Viewlet):
    grok.order(10)
    grok.context(Interface)
    grok.name('dolmen.messages')
    grok.viewletmanager(AboveBody)

    def update(self):
        received = receive()
        if received is not None:
            self.messages = list(received)
        else:
            self.messages = []


class ContextualActions(MenuViewlet):
    grok.context(Interface)
    grok.viewletmanager(Top)
    grok.order(50)

    menu_factory = ContextualMenu
    menu_template = grok.PageTemplateFile('viewlets_templates/menu.pt')

    def compute_actions(self, viewlets):
        for action in viewlets:
            selected = action.__name__ == self.view.__view_name__            
            yield {
                'id': action.__name__,
                'url': not selected and action.url or None,
                'title': action.title,
                'selected': selected,
                'class': (selected and 'selected ' +
                          self.menu.entry_class or self.menu.entry_class),
                }

    def update(self):
        MenuViewlet.update(self)
        if len(self.menu.viewlets) > 1:
            self.actions = self.compute_actions(self.menu.viewlets)
        else:
            self.actions = None

    def render(self):
        return self.menu_template.render(self)


moduleProvides(API.IContextualUI)
__all__ = list(API.IContextualUI)

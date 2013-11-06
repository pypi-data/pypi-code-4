# -*- coding: utf-8 -*-

import grok
import grokcore.layout

from zope.event import notify
from zope.component import getUtility
from zope.interface import Interface
from zope.authentication import interfaces as zai
from dolmen.authentication import UserLogoutEvent
from dolmen.app.authentication import MF as _



class LogoutAction(grok.View):
    grok.title(_(u'Log out'))
    grok.template('logout')
    grok.require('zope.Public')
    grok.context(Interface)

    def update(self):
        if not zai.IUnauthenticatedPrincipal.providedBy(self.request.principal):
            notify(UserLogoutEvent(self.request.principal))
            auth = getUtility(zai.IAuthentication)
            zai.ILogout(auth).logout(self.request)
        self.goto = self.application_url() + '/logout.html'


class LoggedOut(grokcore.layout.Page):
    grok.name('logout.html')
    grok.require("zope.Public")
    grok.context(Interface)

#!/usr/bin/python
# -*- coding: utf-8 -*-

import zope.schema
import zope.interface
import grokcore.view as grok

from zope.event import notify
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.location.interfaces import ILocation

from zeam.form.base import action
from zeam.form.base.markers import SUCCESS, FAILURE
from dolmen.forms import crud
from dolmen.forms.base import Fields
from dolmen.authentication import UserLoginEvent
from dolmen.app.authentication import MF as _


class ILoginForm(zope.interface.Interface):
    """A simple login form interface.
    """
    login = zope.schema.TextLine(
        title=_(u"Username"),
        required=True)

    password = zope.schema.Password(
        title=_(u"Password"),
        required=True)


class Login(crud.ApplicationForm):
    """A very basic implementation of a login form.
    """
    grok.title(_(u"Log in"))
    grok.require('zope.Public')
    grok.context(zope.interface.Interface)

    prefix = ""
    label = _(u"Identify yourself")
    form_name = _(u"Login form")

    @property
    def fields(self):
        fields = Fields(ILoginForm)
        for field in fields:
            field.prefix = u""
        return fields

    @action(_('Log in'))
    def login(self):
        data, errors = self.extractData()
        if errors:
            return FAILURE

        principal = self.request.principal
        if IUnauthenticatedPrincipal.providedBy(principal):
            self.status = _(u"Login failed")
            return FAILURE

        self.flash(_('You are now logged in as ${name}',
                     mapping={"name": principal.id}))
        notify(UserLoginEvent(principal))
        camefrom = self.request.get('camefrom', None)
        if not camefrom:
            if ILocation.providedBy(principal):
                camefrom = absoluteURL(principal, self.request)
            else:
                camefrom = absoluteURL(self.context, self.request)

        self.redirect(camefrom)
        return SUCCESS

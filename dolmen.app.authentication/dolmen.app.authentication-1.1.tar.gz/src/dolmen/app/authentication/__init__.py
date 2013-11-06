# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
MF = MessageFactory('dolmen.app.authentication')
_ = MF

import grok
from dolmen.authentication import IPrincipal
from dolmen.app.authentication import plugins
from dolmen.app.authentication.interfaces import IUser, IChangePassword
from dolmen.app.authentication.browser.validation import UserRegistrationError
from dolmen.app.authentication.permissions import AddUsers, ManageUsers


def initialize_pau(PAU):
    """Initialize an authentication plugin.
    """
    PAU.authenticatorPlugins = ("globalregistry",)
    PAU.credentialsPlugins = ("cookies", "No Challenge if Authenticated")


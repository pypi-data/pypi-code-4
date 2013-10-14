# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getMultiAdapter


class JalonConnecteurIntracursus(BrowserView):

    def getUrlConnexion(self):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.getUrlConnexion()

    def setUrlConnexion(self, urlConnexion):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.setUrlConnexion(self, urlConnexion)

    def getLoginConnexion(self):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.getLoginConnexion()

    def setLoginConnexion(self, loginConnexion):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.setLoginConnexion(loginConnexion)

    def getPasswordConnexion(self):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.getPasswordConnexion()

    def setPasswordConnexion(self, passwordConnexion):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.setPasswordConnexion(passwordConnexion)

    def getVariablesIntracursus(self):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.getVariablesIntracursus()

    def test(self, condition, valeurVrai, valeurFaux):
        return valeurVrai if condition else valeurFaux

    def traductions_fil(self, key):
        intracursus = getToolByName(self, "portal_jalon_intracursus")
        return intracursus.traductions_fil(key)

    def isAnonyme(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()

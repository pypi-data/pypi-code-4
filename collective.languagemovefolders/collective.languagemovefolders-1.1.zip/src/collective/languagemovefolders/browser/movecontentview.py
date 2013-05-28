# -*- coding: utf-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.languagemovefolders import languagemovefoldersMessageFactory as _
from collective.languagemovefolders import utils


class IMoveContentView(Interface):
    """
    MoveContent view interface
    """


class MoveContentView(BrowserView):
    """
    MoveContent browser view
    """
    implements(IMoveContentView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def move_content(self):
        portal = self.portal
        return utils.move_all(portal)

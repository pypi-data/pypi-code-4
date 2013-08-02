# -*- coding: utf-8 -*-

from zope.component import getUtility
from plone.stringinterp.adapters import UrlSubstitution as BaseUrlSubstitution
from plone.stringinterp.adapters import ParentUrlSubstitution as BaseParentUrlSubstitution

from redturtle.smartlink.interfaces.utility import ILinkNormalizerUtility
from collective.stringinterp.smartlink import messageFactory as _

class UrlSubstitution(BaseUrlSubstitution):
    """Plone UrlSubstitution, with ILinkNormalizerUtility"""

    description = _(u'URL (front-end ones)')

    def safe_call(self):
        original_url = BaseUrlSubstitution.safe_call(self)
        linkNormalizerUtility = getUtility(ILinkNormalizerUtility)
        return linkNormalizerUtility.toFrontEnd(original_url)

class OriginalUrlSubstitution(BaseUrlSubstitution):
    """Same Plone adapter, different name"""
    description = _(u'URL (original ones)')

class ParentUrlSubstitution(BaseParentUrlSubstitution):
    """Plone ParentUrlSubstitution, with ILinkNormalizerUtility"""

    description = _(u'Folder URL  (front-end ones)')

    def safe_call(self):
        original_url = BaseParentUrlSubstitution.safe_call(self)
        linkNormalizerUtility = getUtility(ILinkNormalizerUtility)
        return linkNormalizerUtility.toFrontEnd(original_url)

class OriginalParentUrlSubstitution(BaseParentUrlSubstitution):
    """Same Plone adapter, different name"""
    description = _(u'Folder URL (original ones)')

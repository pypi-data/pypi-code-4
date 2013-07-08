# -*- coding: utf-8 -*-

from zope.component import getUtility
from plone.stringinterp.adapters import UrlSubstitution as BaseUrlSubstitution
from plone.stringinterp.adapters import ParentUrlSubstitution as BaseParentUrlSubstitution

from redturtle.smartlink.interfaces.utility import ILinkNormalizerUtility

class UrlSubstitution(BaseUrlSubstitution):
    """Plone UrlSubstitution, with ILinkNormalizerUtility"""
    
    def safe_call(self):
        original_url = BaseUrlSubstitution.safe_call(self)
        linkNormalizerUtility = getUtility(ILinkNormalizerUtility)
        return linkNormalizerUtility.toFrontEnd(original_url)

class ParentUrlSubstitution(BaseParentUrlSubstitution):
    """Plone ParentUrlSubstitution, with ILinkNormalizerUtility"""

    def safe_call(self):
        original_url = BaseParentUrlSubstitution.safe_call(self)
        linkNormalizerUtility = getUtility(ILinkNormalizerUtility)
        return linkNormalizerUtility.toFrontEnd(original_url)

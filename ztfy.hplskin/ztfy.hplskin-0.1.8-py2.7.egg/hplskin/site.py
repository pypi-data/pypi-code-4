### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.hplskin.interfaces import ISiteManagerPresentationInfo
from ztfy.hplskin.layer import IHPLLayer
from ztfy.skin.interfaces import IPresentationTarget

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from zope.proxy import setProxiedObject, ProxyBase

# import local packages
from ztfy.blog.defaultskin.site import SiteManagerPresentation as BaseSiteManagerPresentation, \
                                       SiteManagerIndexView as BaseSiteManagerIndexView
from ztfy.hplskin.menu import HPLSkinDialogMenuItem

from ztfy.hplskin import _


SITE_MANAGER_PRESENTATION_KEY = 'ztfy.hplskin.presentation'


class SiteManagerPresentationViewMenuItem(HPLSkinDialogMenuItem):
    """Site manager presentation menu item"""

    title = _(" :: Presentation model...")


class SiteManagerPresentation(BaseSiteManagerPresentation):
    """Site manager presentation infos"""

    implements(ISiteManagerPresentationInfo)


class SiteManagerPresentationAdapter(ProxyBase):

    adapts(ISiteManager)
    implements(ISiteManagerPresentationInfo)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(SITE_MANAGER_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[SITE_MANAGER_PRESENTATION_KEY] = SiteManagerPresentation()
        setProxiedObject(self, presentation)


class SiteManagerPresentationTargetAdapter(object):

    adapts(ISiteManager, IHPLLayer)
    implements(IPresentationTarget)

    target_interface = ISiteManagerPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SiteManagerIndexView(BaseSiteManagerIndexView):
    """Site manager index page"""

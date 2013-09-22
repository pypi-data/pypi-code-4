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
from ztfy.blog.interfaces.section import ISection
from ztfy.hplskin.interfaces import ISectionPresentationInfo
from ztfy.hplskin.layer import IHPLLayer
from ztfy.skin.interfaces import IPresentationTarget

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from zope.proxy import ProxyBase, setProxiedObject

# import local packages
from ztfy.hplskin.menu import HPLSkinDialogMenuItem
from ztfy.blog.defaultskin.section import SectionPresentation as BaseSectionPresentation, \
                                          SectionIndexView as BaseSectionIndexView

from ztfy.hplskin import _


SECTION_PRESENTATION_KEY = 'ztfy.hplskin.section.presentation'


class SectionPresentationViewMenuItem(HPLSkinDialogMenuItem):
    """Section presentation menu item"""

    title = _(" :: Presentation model...")


class SectionPresentation(BaseSectionPresentation):
    """Section presentation infos"""

    implements(ISectionPresentationInfo)


class SectionPresentationAdapter(ProxyBase):

    adapts(ISection)
    implements(ISectionPresentationInfo)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(SECTION_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[SECTION_PRESENTATION_KEY] = SectionPresentation()
        setProxiedObject(self, presentation)


class SectionPresentationTargetAdapter(object):

    adapts(ISection, IHPLLayer)
    implements(IPresentationTarget)

    target_interface = ISectionPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SectionIndexView(BaseSectionIndexView):
    """Section index page"""

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
from ztfy.blog.interfaces.blog import IBlog
from ztfy.hplskin.interfaces import IBlogPresentationInfo
from ztfy.hplskin.layer import IHPLLayer
from ztfy.skin.interfaces import IPresentationTarget

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from zope.proxy import ProxyBase, setProxiedObject

# import local packages
from ztfy.blog.defaultskin.blog import BlogPresentation as BaseBlogPresentation, \
                                       BlogIndexView as BaseBlogIndexView
from ztfy.hplskin.menu import HPLSkinDialogMenuItem

from ztfy.hplskin import _


BLOG_PRESENTATION_KEY = 'ztfy.hplskin.blog.presentation'


class BlogPresentationViewMenuItem(HPLSkinDialogMenuItem):
    """Blog presentation menu item"""

    title = _(" :: Presentation model...")


class BlogPresentation(BaseBlogPresentation):
    """Blog presentation infos"""

    implements(IBlogPresentationInfo)


class BlogPresentationAdapter(ProxyBase):

    adapts(IBlog)
    implements(IBlogPresentationInfo)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(BLOG_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[BLOG_PRESENTATION_KEY] = BlogPresentation()
        setProxiedObject(self, presentation)


class BlogPresentationTargetAdapter(object):

    adapts(IBlog, IHPLLayer)
    implements(IPresentationTarget)

    target_interface = IBlogPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class BlogIndexView(BaseBlogIndexView):
    """Blog index page"""

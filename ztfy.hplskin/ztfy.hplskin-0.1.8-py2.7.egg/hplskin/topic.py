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
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.blog.interfaces.topic import ITopic
from ztfy.hplskin.interfaces import ISiteManagerPresentationInfo, IBlogPresentationInfo, ITopicPresentationInfo
from ztfy.hplskin.layer import IHPLLayer
from ztfy.skin.interfaces import IPresentationTarget

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from zope.proxy import ProxyBase, setProxiedObject

# import local packages
from ztfy.blog.defaultskin.topic import TopicPresentation as BaseTopicPresentation, \
                                        TopicIndexView as BaseTopicIndexView, \
                                        TopicResourcesView as BaseTopicResourcesView, \
                                        TopicCommentsView as BaseTopicCommentsView
from ztfy.hplskin.menu import HPLSkinDialogMenuItem
from ztfy.utils.traversing import getParent

from ztfy.hplskin import _


TOPIC_PRESENTATION_KEY = 'ztfy.hplskin.topic.presentation'


class TopicPresentationViewMenuItem(HPLSkinDialogMenuItem):
    """Topic presentation menu item"""

    title = _(" :: Presentation model...")


class TopicPresentation(BaseTopicPresentation):
    """Topic presentation infos"""

    implements(ITopicPresentationInfo)


class TopicPresentationAdapter(ProxyBase):

    adapts(ITopic)
    implements(ITopicPresentationInfo)

    def __init__(self, context):
        annotations = IAnnotations(context)
        presentation = annotations.get(TOPIC_PRESENTATION_KEY)
        if presentation is None:
            presentation = annotations[TOPIC_PRESENTATION_KEY] = TopicPresentation()
        setProxiedObject(self, presentation)


class TopicPresentationTargetAdapter(object):

    adapts(ITopic, IHPLLayer)
    implements(IPresentationTarget)

    target_interface = ITopicPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class TopicIndexView(BaseTopicIndexView):
    """Topic index view"""


class TopicResourcesView(BaseTopicResourcesView):
    """Topic resources view"""

    @property
    def resources(self):
        return ITopicPresentationInfo(self.context).linked_resources


class TopicCommentsView(BaseTopicCommentsView):
    """Topic comments view"""

    @property
    def presentation(self):
        if not self.context.commentable:
            return None
        site = getParent(self.context, ISiteManager)
        if site is not None:
            return ISiteManagerPresentationInfo(site)
        blog = getParent(self.context, IBlog)
        if blog is not None:
            return IBlogPresentationInfo(blog)
        return None

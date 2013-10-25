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
from zope.tales.interfaces import ITALESFunctionNamespace

# import local interfaces
from ztfy.skin.interfaces import IPresentationTarget
from ztfy.skin.interfaces.metas import IPageMetasHeaders
from ztfy.skin.tal.interfaces import ISkinTalesAPI, IContentMetasAPI

# import Zope3 packages
from zope.component import queryMultiAdapter
from zope.interface import implements

# import local packages


class SkinTalesAPI(object):

    implements(ISkinTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def presentation(self):
        adapter = queryMultiAdapter((self.context, self.request), IPresentationTarget)
        if adapter is not None:
            interface = adapter.target_interface
            return interface(self.context)


class ContentMetasTalesAPI(object):

    implements(IContentMetasAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def items(self):
        headers = queryMultiAdapter((self.context, self.request), IPageMetasHeaders)
        if headers is None:
            return []
        else:
            return headers.metas

    def render(self):
        headers = queryMultiAdapter((self.context, self.request), IPageMetasHeaders)
        if headers is None:
            return u''
        else:
            return '\n'.join((meta.render() for meta in headers.metas))

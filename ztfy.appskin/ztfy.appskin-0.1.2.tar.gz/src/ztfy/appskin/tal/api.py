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
from ztfy.blog.browser.interfaces.skin import IPresentationTarget
from ztfy.appskin.interfaces import IApplicationBase
from ztfy.appskin.tal.interfaces import IApplicationTalesAPI

# import Zope3 packages
from zope.component import queryMultiAdapter
from zope.interface import implements

# import local packages
from ztfy.utils.traversing import getParent


class ApplicationTalesAPI(object):

    implements(IApplicationTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def application(self):
        return getParent(self.context, IApplicationBase)

    def presentation(self):
        app = self.application()
        if app is not None:
            adapter = queryMultiAdapter((app, self.request), IPresentationTarget)
            if adapter is not None:
                interface = adapter.target_interface
                return interface(app)

### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2013 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
from urllib import urlencode

# import Zope3 interfaces

# import local interfaces
from ztfy.appskin.layer import IAppLayer

# import Zope3 packages
from z3c.table.batch import BatchProvider
from zope.component import adapts
from zope.interface import Interface
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages


class AppskinBatchProvider(BatchProvider):
    """Custom ZTFY.appskin batch provider"""

    adapts(Interface, IAppLayer, Interface)

    def renderBatchLink(self, batch, cssClass=None):
        args = self.getQueryStringArgs()
        args[self.table.prefix + '-batchStart'] = batch.start
        args[self.table.prefix + '-batchSize'] = batch.size
        query = urlencode(sorted(args.items()))
        tableURL = absoluteURL(self.table, self.request)
        idx = batch.index + 1
        css = ' class="btn %s"' % cssClass
        cssClass = cssClass and css or u''
        return '<a href="%s?%s"%s>%s</a>' % (tableURL, query, cssClass, idx)

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
from hurry.query.interfaces import IQuery
from z3c.language.switch.interfaces import II18n
from zope.intid.interfaces import IIntIds

# import local interfaces

# import Zope3 packages
from z3c.jsonrpc.publisher import MethodPublisher
from zope.component import getUtility

# import local packages
from ztfy.utils.catalog.index import Text


class BaseContentSearchView(MethodPublisher):
    """Base content XML-RPC search view"""

    def search(self, query):
        if not query:
            return []
        query_util = getUtility(IQuery)
        intids = getUtility(IIntIds)
        result = []
        for obj in query_util.searchResults(Text(('Catalog', 'title'),
                                                 { 'query': query + '*',
                                                   'ranking': True })):
            result.append({ 'value': str(intids.register(obj)),
                            'caption': II18n(obj).queryAttribute('title') })
        return result

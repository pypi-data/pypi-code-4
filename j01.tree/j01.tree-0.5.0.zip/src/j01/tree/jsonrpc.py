##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
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

"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

from zope.traversing import api
from zope.security.interfaces import Unauthorized
from zope.security.interfaces import Forbidden
from zope.traversing.browser import absoluteURL
from zope.container.interfaces import IReadContainer

from z3c.jsonrpc.publisher import MethodPublisher

from j01.tree.interfaces import JSON_TREE_ID
from j01.tree.interfaces import JSON_TREE_VIEW_NAME
from j01.tree import base
from j01.tree import util


class JSONTreeItems(MethodPublisher, base.IdGeneratorMixin):
    """Returns the data of the childs from the path for the json tree.
    
    This is a simple implementation which uses the traversal concept.
    If you need to lookup items for other conponents then ocntianers,
    e.g. for a widget, you need to implement your own child loader class.
    """

    viewName = JSON_TREE_VIEW_NAME
    j01TreeId = JSON_TREE_ID
    linkHandler = ''

    @property
    def subItems(self):
        """Returns a list of items for the given context."""
        items = []
        keys = []
        append = items.append
        if IReadContainer.providedBy(self.context):
            try:
                keys = list(self.context.keys())
            except(Unauthorized, Forbidden):
                return items
        for name in keys:
            # Only include items we can traverse to
            subItem = api.traverse(self.context, name, None)
            if subItem is not None:
                append(subItem)
        return items

    def hasSubItems(self, item):
        """Returns a True or False if the sub item has subitems."""
        res = False
        if IReadContainer.providedBy(item):
            try:
                if len(item) > 0:
                    res = True
            except(Unauthorized, Forbidden):
                pass
        return res

    def getIconURL(self, item, request, name='icon'):
        return util.getIconURL(item, request, name=name)

    def loadJSONTreeItems(self, id):
        """Returns child information for the object with the given path in a 
           JSON format.

        """
        res = {}
        childs = []
        append = childs.append

        for subItem in self.subItems:

            if self.hasSubItems(subItem):
                hasChilds = True
            else:
                hasChilds = False

            info = {}
            url = absoluteURL(subItem, self.request)
            info['id'] = self.getId(subItem)
            info['content'] = api.getName(subItem)
            info['url'] = url +'/'+ self.viewName
            info['iconURL'] = util.getIconURL(subItem, self.request)
            info['linkHandler'] = self.linkHandler
            info['hasChilds'] = hasChilds
            info['contextURL'] = url
            info['aCSS'] = None
            append(info)
        
        res['treeChilds'] = {'id':id, 'childs':childs}
        
        return res

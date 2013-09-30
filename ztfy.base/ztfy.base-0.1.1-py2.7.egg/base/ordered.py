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
from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList

# import Zope3 interfaces

# import local interfaces
from ztfy.base.interfaces.container import IOrderedContainer

# import Zope3 packages
from zope.container.ordered import OrderedContainer as OrderedContainerBase
from zope.interface import implements
from zope.traversing.api import getName

# import local packages


class OrderedContainer(OrderedContainerBase):

    implements(IOrderedContainer)

    def __init__(self):
        self._data = OOBTree()
        self._order = PersistentList()

    def updateOrder(self, order, iface=None):
        if iface is not None:
            order = [ k for k in order if iface.providedBy(self[k]) ] + \
                    [ getName(v) for v in self.values() if not iface.providedBy(v) ]
        else:
            order = order + [ k for k in self.keys() if k not in order ]
        super(OrderedContainer, self).updateOrder(order)

    def moveUp(self, key):
        keys = list(self.keys())
        index = keys.index(key)
        if index > 0:
            keys[index - 1], keys[index] = keys[index], keys[index - 1]
            self.updateOrder(keys)

    def moveDown(self, key):
        keys = list(self.keys())
        index = keys.index(key)
        if index < len(keys) - 1:
            keys[index + 1], keys[index] = keys[index], keys[index + 1]
            self.updateOrder(keys)

    def moveFirst(self, key):
        keys = list(self.keys())
        index = keys.index(key)
        if index > 0:
            keys = keys[index:index + 1] + keys[:index] + keys[index + 1:]
            self.updateOrder(keys)

    def moveLast(self, key):
        keys = list(self.keys())
        index = keys.index(key)
        if index < len(keys) - 1:
            keys = keys[:index] + keys[index + 1:] + keys[index:index + 1]
            self.updateOrder(keys)

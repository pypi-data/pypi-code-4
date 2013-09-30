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
from zope.container.interfaces import IContainer

# import local interfaces

# import Zope3 packages
from zope.interface import Interface

# import local packages


#
# Containers interfaces
#

class IOrderedContainerOrder(Interface):
    """Ordered containers interface"""

    def updateOrder(self, order):
        """Reset items in given order"""

    def moveUp(self, key):
        """Move given item up"""

    def moveDown(self, key):
        """Move given item down"""

    def moveFirst(self, key):
        """Move given item to first position"""

    def moveLast(self, key):
        """Move given item to last position"""


class IOrderedContainer(IOrderedContainerOrder, IContainer):
    """Marker interface for ordered containers"""

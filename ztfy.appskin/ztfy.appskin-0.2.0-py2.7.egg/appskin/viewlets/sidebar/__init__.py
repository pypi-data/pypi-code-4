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

# import Zope3 interfaces

# import local interfaces
from ztfy.appskin.viewlets.sidebar.interfaces import ISidebarViewletManager, ISidebarMenu

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.skin.viewlet import WeightViewletManagerBase, ViewletBase


class SidebarViewletManager(WeightViewletManagerBase):
    """Sidebar viewlet manager"""

    implements(ISidebarViewletManager)

    def update(self):
        super(SidebarViewletManager, self).update()
        selected = [ menu for menu in self.viewlets if menu.selected ]
        self.selected = selected[0] if selected else None


class SidebarMenu(ViewletBase):
    """Sidebar menu"""

    implements(ISidebarMenu)

    cssClass = None
    label = None

    def update(self):
        self.selected = self.request.getURL().endswith(self.viewURL)

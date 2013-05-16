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
from ztfy.appskin.viewlets.usernav.interfaces import IUserNavigationViewletManager, IUserNavigationMenu

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.skin.viewlet import ViewletBase, WeightViewletManagerBase

from ztfy.appskin import _


class UserNavigationViewletManager(WeightViewletManagerBase):
    """User navigation viewlet manager"""

    implements(IUserNavigationViewletManager)


class UserNavigationMenu(ViewletBase):
    """User navigation menu"""

    implements(IUserNavigationMenu)

    cssClass = None
    label = None


#
# Standard user actions
#

class UserManagementAction(UserNavigationMenu):
    """User access to management interface"""

    title = _("Access management interface")
    label = _("Admin.")
    viewURL = "@@properties.html"


class UserLogoutAction(UserNavigationMenu):
    """User logout action"""

    title = _("Quit application")
    label = _("Logout")
    viewURL = "@@logout.html"

    def render(self):
        if self.request.principal.id == 'zope.anybody':
            return u''
        return super(UserLogoutAction, self).render()

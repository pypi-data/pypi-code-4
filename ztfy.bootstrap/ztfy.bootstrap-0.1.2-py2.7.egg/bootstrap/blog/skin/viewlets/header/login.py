### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
import copy

# import Zope3 interfaces
from zope.publisher.interfaces.browser import IBrowserSkinType

# import local interfaces
from ztfy.skin.interfaces import IDefaultView

# import Zope3 packages
from zope.component import queryUtility, queryMultiAdapter
from zope.publisher.browser import applySkin

# import local packages
from ztfy.skin.viewlet import ViewletBase


class LoginViewlet(ViewletBase):

    @property
    def manage_url(self):
        skin = queryUtility(IBrowserSkinType, 'ZTFY.BO')
        if skin is not None:
            fake = copy.copy(self.request)
            applySkin(fake, skin)
        else:
            fake = self.request
        adapter = queryMultiAdapter((self.context, fake, self.__parent__), IDefaultView)
        if adapter is not None:
            return adapter.getAbsoluteURL()

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
from datetime import datetime

# import Zope3 interfaces

# import local interfaces
from ztfy.bootstrap.blog.skin.viewlets.footer.interfaces import IFooterViewletManager

# import Zope3 packages
from zope.interface import implements
from zope.viewlet.manager import WeightOrderedViewletManager

# import local packages
from ztfy.blog.browser.viewlets import BaseViewlet


class FooterViewletManager(WeightOrderedViewletManager):
    """Footer viewlet manager"""

    implements(IFooterViewletManager)


class FooterSignatureViewlet(BaseViewlet):
    """Footer signature viewlet"""

    @property
    def year(self):
        return datetime.now().year

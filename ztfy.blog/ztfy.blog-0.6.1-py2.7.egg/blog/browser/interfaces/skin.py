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

# import local interfaces
from ztfy.skin.interfaces import IBaseIndexView

# import Zope3 packages
from zope.interface import Interface

# import local packages


# Base front-office views

class ISiteManagerIndexView(IBaseIndexView):
    """Site manager index view marker interface"""


class IBlogIndexView(IBaseIndexView):
    """Blog index view marker interface"""


class IBlogFolderIndexView(IBaseIndexView):
    """Blog folder index view marker interface"""


class ISectionIndexView(IBaseIndexView):
    """Section index view marker interface"""


class ITopicIndexView(Interface):
    """Topic index view marker interface"""


class ICategoryIndexView(Interface):
    """Category index view marker interface"""

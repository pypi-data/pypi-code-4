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
from ztfy.base.interfaces.container import IOrderedContainer
from ztfy.blog.defaultskin.interfaces import ISiteManagerPresentationInfo as IBaseSiteManagerPresentationInfo, \
                                             IBlogPresentationInfo as IBaseBlogPresentationInfo, \
                                             ISectionPresentationInfo as IBaseSectionPresentationInfo, \
                                             ITopicPresentationInfo as IBaseTopicPresentationInfo

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface

# import local packages
from ztfy.file.schema import ImageField

from ztfy.hplskin import _


#
# Contents presentation infos
#

class ISiteManagerPresentationInfo(IBaseSiteManagerPresentationInfo):
    """Site manager presentation info"""


class IBlogPresentationInfo(IBaseBlogPresentationInfo):
    """Blog presentation info"""


class ISectionPresentationInfo(IBaseSectionPresentationInfo):
    """Section presentation info"""


class ITopicPresentationInfo(IBaseTopicPresentationInfo):
    """Topic presentation info"""


#
# Banners management
#

class IBannerImage(Interface):
    """Site manager banner interface"""

    image = ImageField(title=_("Image data"),
                       description=_("This attribute holds image data"),
                       required=True)


class ITopBannerImageAddFormMenuTarget(Interface):
    """Marker interface for banner image add form menu target"""


class ILeftBannerImageAddFormMenuTarget(Interface):
    """Marker interface for banner image add form menu target"""


class IBannerManager(IOrderedContainer):
    """Banner manager marker interface"""

    contains(IBannerImage)


class IBannerManagerContentsView(Interface):
    """Banner manager contents view marker interface"""

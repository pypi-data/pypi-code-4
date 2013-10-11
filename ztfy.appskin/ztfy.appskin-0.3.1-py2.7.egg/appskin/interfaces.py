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

# import Zope3 interfaces

# import local interfaces
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.interface import Interface, Attribute

# import local packages
from ztfy.file.schema import ImageField
from ztfy.i18n.schema import I18nTextLine

from ztfy.appskin import _


#
# Application base marker interface
#

class IApplicationBase(Interface):
    """Base application marker interface"""


class IApplicationResources(Interface):
    """Application resources interface"""

    resources = Attribute(_("Tuple of Fanstatic resources needed by application's layout"))


#
# Marker interface for anonymous pages
#

class IAnonymousPage(Interface):
    """Marker interface for anonymous pages"""


class ILoginView(Interface):
    """Login page marker interface"""


class ILoginViewHelp(Interface):
    """Login view help interface"""

    help = Attribute(_("Help text"))


#
# Base application presentation info
#

class IApplicationPresentationInfo(II18nAttributesAware):
    """Base application presentation info"""

    site_icon = ImageField(title=_("Application icon"),
                           description=_("Site 'favicon' image"),
                           required=False)

    logo = ImageField(title=_("Logo image"),
                      required=False)

    footer_text = I18nTextLine(title=_("Footer text"),
                               required=False)

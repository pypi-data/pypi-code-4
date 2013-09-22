### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.skin.interfaces import ISkinnable as ISkinnableBase

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import Choice, TextLine, List
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# import local packages
from ztfy.i18n.schema import I18nTextLine, I18nText, I18nImage, I18nCthumbImage
from ztfy.security.schema import PrincipalList

# BBB: These imports are kept for database compatibility
from ztfy.base.interfaces import IPathElements, IBaseContentType, IBaseContent, IMainContent
# ##

from ztfy.blog import _


#
# Skinnable contents
#

class ISkinnable(ISkinnableBase):
    """Custom skinnable interface allowing skin selection"""

    skin = Choice(title=_("Skin name"),
                  description=_("Name of the skin applied to the current context ; WARNING: inheritance can only work correctly in specific contexts..."),
                  required=False,
                  vocabulary="ZTFY blog skins")


class ITopicElement(Interface):
    """Marker interface for topics elements"""


class IBaseContentRoles(Interface):
    """Site manager roles"""

    administrators = PrincipalList(title=_("Site administrators"),
                                   description=_("List of site's administrators"),
                                   required=False)

    contributors = PrincipalList(title=_("Site contributors"),
                                 description=_("List of site's contributors"),
                                 required=False)


#
# Workflow management
#

STATUS_DRAFT = 0
STATUS_PUBLISHED = 1
STATUS_RETIRED = 2
STATUS_ARCHIVED = 3
STATUS_DELETED = 4

STATUS_IDS = [ 'draft', 'published', 'retired', 'archived', 'deleted' ]
STATUS_LABELS = (_("Draft"), _("Published"), _("Retired"), _("Archived"), _("Deleted"))

STATUS_VOCABULARY = SimpleVocabulary([SimpleTerm(i, i, t) for i, t in enumerate(STATUS_LABELS)])

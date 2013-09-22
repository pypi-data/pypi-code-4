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

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import List, Object

# import local packages

from ztfy.skin import _


class IBaseMeta(Interface):
    """Base meta header interface"""

    def render(self):
        """Render given meta header"""


class IHTTPEquivMetaHeader(IBaseMeta):
    """HTTP-Equiv meta header interface"""

    http_equiv = Attribute(_("HTTP equiv header"))

    value = Attribute(_("Meta content value"))


class IContentMetaHeader(IBaseMeta):
    """Content meta header interface"""

    name = Attribute(_("Meta name"))

    value = Attribute(_("Meta content value"))


class IPropertyMetaHeader(IBaseMeta):
    """Property meta header interface"""

    property = Attribute(_("Meta property"))

    value = Attribute(_("Meta content value"))


class ILinkMetaHeader(IBaseMeta):
    """Link meta header interface"""

    rel = Attribute(_("Meta rel attribute"))

    type = Attribute(_("Meta type attribute"))

    href = Attribute(_("Meta link target"))


class IContentMetasHeaders(Interface):
    """Content metas headers interface"""

    metas = List(title=_("Metas list"),
                 description=_("Full list of metas associated with this content"),
                 value_type=Object(schema=IContentMetaHeader))


class IPageMetasHeaders(Interface):
    """Full list of metas headers for given content"""

    metas = List(title=_("Metas list"),
                 description=_("Full list of metas associated with this content"),
                 value_type=Object(schema=IContentMetaHeader))

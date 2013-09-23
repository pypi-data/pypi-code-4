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


# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine, BytesLine, Bool, Int

# import local packages

from ztfy.alchemy import _


class IAlchemyEngineUtility(Interface):
    """SQLAlchemy engine utility interface"""

    name = TextLine(title=_("Name"),
                    required=False)

    dsn = TextLine(title=_('DSN'),
                   required=True,
                   default=u'sqlite://')

    echo = Bool(title=_('Echo SQL'),
                required=True,
                default=False)

    pool_size = Int(title=_("Pool size"),
                    required=True,
                    default=25)

    pool_recycle = Int(title=_("Pool recycle time"),
                       required=True,
                       default=-1)

    register_geotypes = Bool(title=_("Register GEOTypes"),
                             required=True,
                             default=False)

    register_opengis = Bool(title=_("Register OpenGIS"),
                            required=True,
                            default=False)

    encoding = BytesLine(title=_('Encoding'),
                         required=True,
                         default='utf-8')

    convert_unicode = Bool(title=_('Convert Unicode'),
                           required=True,
                           default=False)


class IAlchemyBaseObject(Interface):
    """SQLAlchemy object base interface"""

    _sa_instance_state = Attribute(_("SQLAlchemy instance state"))

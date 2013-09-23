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
from zope.interface import Interface
from zope.schema import TextLine, Bool, Int
from zope.configuration.fields import GlobalObject

# import local packages

from ztfy.alchemy import _


class IEngineDirective(Interface):
    """Define a new SQLAlchemy engine"""

    dsn = TextLine(title=_('Database URL'),
                   description=_('RFC-1738 compliant URL for the database connection'),
                   required=True)

    name = TextLine(title=_('Engine name'),
                    description=_('Empty if this engine is the default engine.'),
                    required=False,
                    default=u'')

    echo = Bool(title=_('Echo SQL statements'),
                required=False,
                default=False)

    pool_size = Int(title=_("Pool size"),
                    description=_("SQLAlchemy connections pool size"),
                    required=False,
                    default=25)

    pool_recycle = Int(title=_("Pool recycle time"),
                       description=_("SQLAlchemy connection recycle time (-1 for none)"),
                       required=False,
                       default= -1)

    register_geotypes = Bool(title=_("Register GeoTypes"),
                             description=_("Should engine register PostGis GeoTypes"),
                             default=False)

    register_opengis = Bool(title=_("Register OpenGIS"),
                            description=_("Should engine register OpenGIS types"),
                            default=False)


class ITableAssignDirective(Interface):
    """Assign a table to a given engine"""

    table = TextLine(title=_("Table name"),
                     description=_("Name of the table to assign"),
                     required=True)

    engine = TextLine(title=_("SQLAlchemy engine"),
                      description=_("Name of the engine to connect the table to"),
                      required=True)


class IClassAssignDirective(Interface):
    """Assign a table to a given engine"""

    class_ = GlobalObject(title=_("Class name"),
                          description=_("Name of the class to assign"),
                          required=True)

    engine = TextLine(title=_("SQLAlchemy engine"),
                      description=_("Name of the engine to connect the table to"),
                      required=True)

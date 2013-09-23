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
from ztfy.alchemy.interfaces import IAlchemyEngineUtility

# import Zope3 packages
from zope.component.security import PublicPermission
from zope.component.zcml import utility

# import local packages
from ztfy.alchemy.engine import AlchemyEngineUtility, assignTable, assignClass


def engine(context, dsn, name='', echo=False, pool_size=25, pool_recycle= -1, register_geotypes=False, register_opengis=False, **kw):
    engine = AlchemyEngineUtility(name, dsn, echo=echo, pool_size=pool_size, pool_recycle=pool_recycle, register_geotypes=register_geotypes, register_opengis=register_opengis, **kw)
    utility(context, IAlchemyEngineUtility, engine, permission=PublicPermission, name=name)


def connectTable(context, table, engine):
    context.action(discriminator=('ztfy.alchemy.table', table),
                   callable=assignTable,
                   args=(table, engine, False))


def connectClass(context, class_, engine):
    context.action(discriminator=('ztfy.alchemy.class', class_),
                   callable=assignClass,
                   args=(class_, engine, False))

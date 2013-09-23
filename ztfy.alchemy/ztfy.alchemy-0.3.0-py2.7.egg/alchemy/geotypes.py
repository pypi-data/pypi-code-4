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


import sqlalchemy

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from GeoTypes import OGGeoTypeFactory, WKBParser


class PostGisWKBFactory(object):

    def __init__(self):
        pass

    def __call__(self, s=None):
        factory = OGGeoTypeFactory()
        parser = WKBParser(factory)
        parser.parseGeometry(s)
        return factory.getGeometry()


class GeometryType(sqlalchemy.types.TypeEngine):

    def __init__(self, SRID, typeName, dimension):
        super(GeometryType, self).__init__()
        self.mSrid = SRID
        self.mType = typeName.upper()
        self.mDim = dimension
        self.bfact = PostGisWKBFactory()

    def __repr__(self):
        return "%s:%s-%s(%s)" % (self.__class__.__name__, self.mType, self.mDim, self.mSrid)

    def get_col_spec(self):
        return "GEOMETRY"


class GeometryPOINT(GeometryType):

    def __init__(self, srid):
        super(GeometryPOINT, self).__init__(srid, "POINT", 2)


class GeometryLINESTRING(GeometryType):

    def __init__(self, srid):
        super(GeometryPOINT, self).__init__(srid, "LINESTRING", 2)

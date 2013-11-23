###############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: item.py 3838 2013-09-07 07:05:28Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.location.interfaces

import m01.mongo.interfaces
from m01.mongo import LOCAL
from m01.mongo.fieldproperty import MongoFieldProperty

import m01.zfs.base
from m01.zfs import interfaces


class FileStorageItem(m01.zfs.base.FileItemBase):
    """Simple mongo file item.
    
    This FileStorageItem will use the mongo ObjectId as the __name__. This
    means you can't set an own __name__ value for this object.

    Implement your own IFileStorageItem with the attributes you need and the
    relevant chunks collection.
    """

    zope.interface.implements(interfaces.IFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


class FileContainerItem(m01.zfs.base.FileItemBase):
    """File container item.

    Implement your own IFileContainerItem with the attributes you need and the
    relevant chunks collection.
    """

    zope.interface.implements(interfaces.IFileStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = []

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(
        zope.location.interfaces.ILocation['__name__'])

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
$Id: base.py 3838 2013-09-07 07:05:28Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import m01.mongo.base
from m01.mongo.fieldproperty import MongoFieldProperty
from m01.mongo.fieldproperty import MongoBinaryProperty

from m01.zfs import interfaces
import m01.zfs.chunker


class FileBase(object):
    """File base class"""

    # file data
    fname = MongoFieldProperty(interfaces.IFile['fname'])
    data = MongoBinaryProperty(interfaces.IFile['data'])
    size = MongoFieldProperty(interfaces.IFile['size'])
    md5 = MongoFieldProperty(interfaces.IFile['md5'])
    date = MongoFieldProperty(interfaces.IFile['date'])

    # content data
    ctype = MongoFieldProperty(interfaces.IFile['ctype'])
    csize = MongoFieldProperty(interfaces.IFile['csize'])

    @property
    def collection(self):
        """Returns a mongodb collection for store file meta and chunks data."""
        raise NotImplementedError(
            "Subclass must implement the collection attribute")

    def getFileWriter(self):
        """Returns a IChunkReader"""
        return m01.zfs.chunker.ChunkWriter(self)

    def getFileReader(self):
        """Returns a IChunkReader"""
        return m01.zfs.chunker.ChunkReader(self)

    def applyFileUpload(self, fileUpload):
        """Apply FileUpload given from request publisher"""
        if not fileUpload or not fileUpload.filename:
            # empty string or None means no upload
            raise ValueError("Missing file upload data")
        writer = self.getFileWriter()
        writer.add(fileUpload)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.__name__)


class FileItemBase(FileBase, m01.mongo.base.MongoItemBase):
    """Mongo file item base class."""

    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified',
                  'fname', 'data', 'size', 'md5', 'date',
                  'ctype', 'csize']

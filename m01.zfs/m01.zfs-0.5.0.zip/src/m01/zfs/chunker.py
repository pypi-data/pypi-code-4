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
$Id: chunker.py 3881 2013-11-23 19:06:24Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import datetime
import hashlib
import logging
import math
import zlib
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import zope.interface
from zope.contenttype import guess_content_type

from m01.mongo import UTC

import m01.zfs.exceptions
from m01.zfs import interfaces


logger = logging.getLogger('m01.zfs')

_SEEK_SET = os.SEEK_SET
_SEEK_CUR = os.SEEK_CUR
_SEEK_END = os.SEEK_END

BLOCK_SIZE = 16 * 1024 * 1024 # 16 MB


def extractFileName(filename):
    """Stip out path in filename (happens in IE upload)"""
    # strip out the path section even if we do not remove them
    # later, because we just need to check the filename extension.
    cleanFileName = filename.split('\\')[-1]
    cleanFileName = cleanFileName.split('/')[-1]
    dottedParts = cleanFileName.split('.')
    if len(dottedParts) <= 1:
        raise m01.zfs.exceptions.MissingFileNameExtension()
    return cleanFileName


def getContentType(filename):
    """Returns the content type based on the given filename"""
    return guess_content_type(filename)[0]


def ChunkIterator(reader):
    while True:
        chunk = reader.read(BLOCK_SIZE)
        if not chunk:
            reader.close()
            raise StopIteration()
        yield chunk
    reader.close()


class ChunkLogging(object):
    """Logging support"""

    def _doLog(self, msg, level=logging.DEBUG):
        logger.log(level, '%s %s %s' % (self._id, self.__class__.__name__, msg))

    def info(self, msg):
        self._doLog(msg, logging.INFO)

    def debug(self, msg):
        self._doLog(msg, logging.DEBUG)

    def error(self, msg):
        self._doLog(msg, logging.ERROR)

    
class ChunkWriterBase(ChunkLogging):
    """File chunk writer base class
    
    Note: this reader write plain data to compressed data
    """

    zope.interface.implements(interfaces.IChunkWriter)

    def __init__(self, encoding=None):
        """Setup ChunkWriterBase basics"""
        self.encoding = encoding
        self._closed = False

    @property
    def closed(self):
        """Return close marker"""
        return self._closed

    def close(self):
        """Mark the file as closed

        A closed file cannot be written any more. Calling `close` more than
        once is allowed.
        """
        if not self._closed:
            self._closed = True

    def validate(self, fileUpload):
        """Validate file upload item"""
        if self._closed:
            raise ValueError("cannot write to a closed file")
        elif not fileUpload or not fileUpload.filename:
            # empty string or None or missing filename means no upload given
            raise ValueError("Missing file upload data")

    def setFileName(self, filename):
        """Set filename (hook for adjust the given filename)"""
        self.context.fname = unicode(filename)

    def setContentType(self, ctype):
        """Set content type (hook for adjust the given type)"""
        self.context.ctype = unicode(ctype)

    def write(self, data):
        """Write data to IFile context"""
        if self._closed:
            raise ValueError("cannot write to a closed file")
        try:
            # file-like
            read = data.read
        except AttributeError:
            # string
            if not isinstance(data, basestring):
                raise TypeError(
                    "can only write strings or file-like objects and not %s" % 
                        type(data))
            if isinstance(data, unicode):
                if self.encoding is not None:
                    data = data.encode(self.encoding)
                else:
                    raise TypeError("must specify an encoding for file in "
                                    "order to write unicode")
            read = StringIO(data).read

        # write data to context
        data = read()
        # before comporess, set content size
        self.csize = len(data)
        # calculate and set md5
        digester = hashlib.md5()
        digester.update(data)
        data = zlib.compress(data)
        # set comppressed data and size
        self.size = len(data)
        self.context.data = data
        return digester

    def addData(self, data, fname, ctype):
        """Add file like item or string data as chunk"""
        success = False
        try:
            # make sure we begin at the start
            digester = self.write(data)
            md5 = digester.hexdigest()
            # marker for successfully added chunk
            success = True
        except Exception, e:
            self.error('add caused an error')
            # and raise the exception
            raise e
        if success:
            # apply metadata to adapted IFile
            self.setFileName(fname)
            self.setContentType(ctype)
            self.context.md5 = unicode(md5)
            self.context.size = self.size
            self.context.csize = self.csize
            self.context.date = datetime.datetime.now(UTC)
            self.debug('success')

    def add(self, fileUpload):
        """Add file upload item as chunk"""
        success = False
        self.validate(fileUpload)
        fname = extractFileName(fileUpload.filename)
        ctype = getContentType(fname)
        try:
            # make sure we begin at the start
            fileUpload.seek(0)
            digester = self.write(fileUpload)
            md5 = digester.hexdigest()
            # marker for successfully added chunk
            success = True
        except Exception, e:
            self.error('add caused an error')
            # and raise the exception
            raise e
        finally:
            self.close()
        if success:
            # apply metadata to adapted IFile
            self.setFileName(fname)
            self.setContentType(ctype)
            self.context.md5 = unicode(md5)
            self.context.size = self.size
            self.context.date = datetime.datetime.now(UTC)
            self.debug('success')

    def __enter__(self):
        """Support for the context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for the context manager protocol.

        Close the file and allow exceptions to propogate.
        """
        self.close()
        # propogate exceptions
        return False


class ChunkWriter(ChunkWriterBase):
    """File chunk writer adapter"""

    zope.component.adapts(interfaces.IFile)

    def __init__(self, context, encoding=None):
        """Setup ChunkWriter based on adapted IFile context"""
        super(ChunkWriter, self).__init__(encoding)
        self.context = context
        self._id = context._id
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)


class ChunkReaderBase(ChunkLogging):
    """File chunk reader adapter base class
    
    NOTE: this reader loads uncompresses zlib data into a buffer attribute
    and reads them with the chunk size used in read method.
    """

    zope.interface.implements(interfaces.IChunkReader)

    size = None
    md5 = None
    fname = None
    ctype = None
    csize = None
    date = None

    def __init__(self):
        self._buffer = None

    def _reset(self):
        self._buffer = None

    @property
    def __name__(self):
        """simply map filename as __name__ (common in zope)"""
        return self.context.fname

    def close(self):
        """Support file-like API"""
        self._reset()

    def readBuffer(self, size=-1):
        """Read from buffer"""
        if size == 0:
            data = ""
        elif size < 0:
            data = self._buffer
            self._buffer = ""
        else:
            data = self._buffer[:size]
            self._buffer = self._buffer[size:]
        return data

    def read(self, size=-1):
        """Read at most `size` bytes from the decompressed data

        If size is negative or omitted all data get returned
        """
        if self._buffer is None:
            self._buffer = zlib.decompress(self.context.data, zlib.MAX_WBITS)

        return self.readBuffer(size)

    def readline(self, size=-1):
        """Read one line or up to `size` bytes from the file data"""
        # hopefully nobody is using this slow access
        bytes = ""
        while len(bytes) != size:
            byte = self.read(1)
            bytes += byte
            if byte == "" or byte == "\n":
                break
        return bytes

    def tell(self):
        """Return the current position of this file"""
        raise NotImplementedError("tell is not supported yet")

    def seek(self, pos, whence=_SEEK_SET):
        """Set the current position of this file"""
        if pos != 0:
            raise NotImplementedError(
                "Only seek with position 0 is implemented")
        self._reset()

    def __iter__(self):
        """Return an iterator over all of this file's data"""
        # return iterator
        return ChunkIterator(self)

    def __enter__(self):
        """Makes it possible to use with the context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Makes it possible to use with the context manager protocol"""
        return False


class ChunkReader(ChunkReaderBase):
    """File chunk reader adapter"""

    zope.component.adapts(interfaces.IFile)

    def __init__(self, context):
        """Setup chunk reader based on adapted context"""
        super(ChunkReader, self).__init__()
        self.context = context
        self._id = context._id
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        self.size = self.context.size
        self.md5 = self.context.md5
        self.fname = self.context.fname
        self.ctype = self.context.ctype
        self.csize = self.context.csize
        self.date = self.context.date


class ChunkDataReader(ChunkReaderBase):
    """Chunk data reader based on given mongodb file data"""

    def __init__(self, data):
        """Setup chunk reader based on given file data"""
        super(ChunkDataReader, self).__init__()
        self._id = data['_id']
        if not self._id:
            raise ValueError("Missing mongo ObjectId", self._id)
        self.size = data['size']
        self.md5 = data['md5']
        self.fname = data['fname']
        self.ctype = data['ctype']
        self.csize = data['csize']
        self.date = data['date']


def getChunkDataReader(collection, query):
    """Lookup a file and return a ChunkDataReader"""
    # get data
    data = collection.find_one(query)
    return ChunkDataReader(data)

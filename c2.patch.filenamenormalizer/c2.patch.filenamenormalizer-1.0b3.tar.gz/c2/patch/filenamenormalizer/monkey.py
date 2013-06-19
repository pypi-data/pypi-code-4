#!/usr/bin/env python
# encoding: utf-8
"""
monkey.py

Created by Manabu Terada on 2010-01-08.
Copyright (c) 2010 CMScom. All rights reserved.
"""

import urllib
from email.Message import Message as emailMessage
from Acquisition import aq_get
from webdav.common import rfc1123_date
from Products.Archetypes.Field import FileField
#from Products.Archetypes.utils import contentDispositionHeader
from config import *

from logging import getLogger
logger = getLogger(__name__)
info = logger.info

try:
    from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
    from plone.i18n.normalizer import FILENAME_REGEX
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False
try:
    from plone.app.blob import field
    from plone.app.blob.download import handleIfModifiedSince, handleRequestRange
    IS_BLOB = True
except ImportError:
    IS_BLOB = False
try:
    from c2.app.zipdownload.event import FileDownloadEvent
    HAS_ZIPDOWNLOAD = True
except ImportError:
    HAS_ZIPDOWNLOAD = False
if HAS_ZIPDOWNLOAD:
    from zope.event import notify


def contentDispositionHeader(disposition, charset='utf-8', language=None, **kw):
    """Return a properly quoted disposition header

    Originally from CMFManagedFile/content.py.
    charset default changed to utf-8 for consistency with the rest of Archetypes.
    
    Original Products/Archetypes/utils.py 
    """
    for key, value in kw.items():
        # stringify the value
        if isinstance(value, unicode):
            value = value.encode(charset)
        else:
            value = str(value)
            # raise an error if the charset doesn't match
            unicode(value, charset, 'strict')
        # if any value contains 8-bit chars, make it an
        # encoding 3-tuple for special treatment by
        # Message.add_header() (actually _formatparam())
        try:
            unicode(value, 'us-ascii', 'strict')
        except UnicodeDecodeError:
            value = (charset, language, value)
        kw[key] = value

    m = emailMessage()
    m.add_header('content-disposition', disposition, **kw)
    return m['content-disposition']

def get_header_value(ua, filename, instance):

    if 'MSIE' in ua:        
        if FILE_NORMALIZER and not IE_NORMALIZE:
            filename = IUserPreferredFileNameNormalizer(instance.REQUEST).normalize(
                    unicode(filename, instance.getCharset()))
            base = filename
            ext = ""
            m = FILENAME_REGEX.match(filename)
            if m is not None:
                base = m.groups()[0]
                ext  = m.groups()[1]
            if len(base) > 8:
                base = base[:8]
            if ext:
                base = base + '.' + ext
            header_value = contentDispositionHeader(
                            disposition='attachment',
                            filename=base,
                            )
        elif not JA_DEPENDENCE:
            filename = urllib.quote(
                unicode(filename, instance.getCharset()).encode('utf-8', 'replace'))
            header_value = contentDispositionHeader(
                            disposition='attachment',
                            filename=filename,
                            )
        else:
            filename = unicode(filename, instance.getCharset()).encode('shift_jis', 'replace')
            m = emailMessage()
            disposition='attachment'
            kw = {'filename' : filename}
            m.add_header('content-disposition', disposition, **kw)
            header_value = m['content-disposition'].replace("\\\\", "\\")
    elif 'Chrome' in ua:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
        m = emailMessage()
        disposition='attachment'
        kw = {'filename' : filename}
        m.add_header('content-disposition', disposition, **kw)
        header_value = m['content-disposition']
    elif 'Firefox' in ua:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
        m = emailMessage()
        disposition='attachment'
        kw = {'filename' : filename}
        m.add_header('content-disposition', disposition, **kw)
        header_value = m['content-disposition']
    elif 'Safari' in ua:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
        m = emailMessage()
        disposition='attachment'
        kw = {'filename' : filename}
        m.add_header('content-disposition', disposition, **kw)
        header_value = m['content-disposition']
    elif 'Opera' in ua:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
        m = emailMessage()
        disposition='attachment'
        kw = {'filename' : filename}
        m.add_header('content-disposition', disposition, **kw)
        header_value = m['content-disposition']
    else:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
        header_value = contentDispositionHeader(
                            disposition='attachment',
                            filename=filename,
                            charset=charset, language=language
                            )
    return header_value

def ng_download(self, instance, REQUEST=None, RESPONSE=None, no_output=False):
    """Kicks download.

    Writes data including file name and content type to RESPONSE
    """
    if HAS_ZIPDOWNLOAD:
        notify(FileDownloadEvent(instance))
    file = self.get(instance, raw=True)
    if not REQUEST:
        REQUEST = aq_get(instance, 'REQUEST')
    ua = REQUEST.get('HTTP_USER_AGENT')

    if not RESPONSE:
        RESPONSE = REQUEST.RESPONSE
    filename = self.getFilename(instance)
    if filename is not None:
        header_value = get_header_value(ua, filename, instance)
        RESPONSE.setHeader("Content-disposition", header_value)
    if no_output:
        return file
    return file.index_html(REQUEST, RESPONSE)


def blob_index_html(self, instance, REQUEST=None, RESPONSE=None, disposition='inline'):
    """ make it directly viewable when entering the objects URL 
    Original plone.app.blob.field.py
    """
    if HAS_ZIPDOWNLOAD:
        notify(FileDownloadEvent(instance))
    if REQUEST is None:
        REQUEST = instance.REQUEST
    ua = REQUEST.get('HTTP_USER_AGENT')
    if RESPONSE is None:
        RESPONSE = REQUEST.RESPONSE
    blob = self.getUnwrapped(instance, raw=True)    # TODO: why 'raw'?
    RESPONSE.setHeader('Last-Modified', rfc1123_date(instance._p_mtime))
    RESPONSE.setHeader('Content-Type', self.getContentType(instance))
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
    if handleIfModifiedSince(instance, REQUEST, RESPONSE):
        return ''
    length = blob.get_size()
    RESPONSE.setHeader('Content-Length', length)
    filename = self.getFilename(instance)
    if filename is not None:
        # filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
        #     unicode(filename, instance.getCharset()))
        # header_value = contentDispositionHeader(
        #     disposition=disposition,
        #     filename=filename)
        # RESPONSE.setHeader("Content-disposition", header_value)
        header_value = get_header_value(ua, filename, instance)
        RESPONSE.setHeader("Content-disposition", header_value)
    range = handleRequestRange(instance, length, REQUEST, RESPONSE)
    return blob.getIterator(**range)


FileField.download = ng_download
info('patched %s', str(FileField.download))

if IS_BLOB:
    field.BlobField.index_html = blob_index_html
    info('patched %s', str(field.BlobField.index_html))
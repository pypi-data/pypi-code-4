#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import os
from datetime import datetime
from uuid import uuid4
from mimetypes import add_type, guess_type, guess_extension
from formv.utils.iterators import StreamIterator

__all__ = ('BaseFileInfo','ExistingFileInfo','ReusedFileInfo','UploadedFileInfo',)

add_type('text/csv', '.csv', False)

image_mime_types = ('image/bmp','image/gif','image/jpeg','image/pjpeg',
                    'image/pipeg','image/png','image/x-png','image/tiff',
                    'image/x-tiff','image/x-xbm','image/x-xbitmap',
                    'image/x-pict','image/x-portable-anymap',
                    'image/x-portable-bitmap','image/x-portable-graymap',
                    'image/x-portable-pixmap','image/x-rgb','image/x-win-bmp')

class BaseFileInfo(object):
    """ base file-info """
    html_field = None
    file_object = None              
    dir_path = None
    orig_name = None
    guid_name = None
    file_size = None
    file_date = None
    mime_type = None
    file_ext = None
    zip_size = None

    def _file_name(self):
        return (self.guid_name + self.file_ext)
    file_name = property(_file_name) 
    
    def _zip_name(self):
        if self.zip_size is not None:
            return (self.guid_name + '.zip')
    zip_name = property(_zip_name)
    
    def _thumb_name(self):
        if self.mime_type in image_mime_types:
            return self.guid_name + '_th' + self.file_ext
    thumb_name = property(_thumb_name)
    
    def _file_path(self):
        return os.path.join(self.dir_path, self._file_name())
    file_path = property(_file_path)
    
    def _zip_path(self):
        if self.zip_size is not None:
            return os.path.join(self.dir_path, self._zip_name())
    zip_path = property(_zip_path)
    
    def _thumb_path(self):
        if self.mime_type in image_mime_types:
            return os.path.join(self.dir_path, self._thumb_name())
    thumb_path = property(_thumb_path)
    
    def _guess_mimetype(self):
        return guess_type(self.orig_name, False)[0] or 'application/octet-stream'
    
    def _guess_name(self):
        return self.orig_name.rsplit('.', 1)[0]
    
    def _guess_extension(self):
        parts = self.orig_name.rsplit('.', 1)
        if len(parts) == 2:
            return '.' + parts[1]
        return guess_extension(self.mime_type, False) or ''
   
    def __str__(self):
        s = ''
        for k in sorted(self.keys()):
            s += '\n' + ' '*4 + str(k) + ': ' + repr(getattr(self, k))
        return s 
    
    __repr__ = __str__
    
    def get(self, k, default=None):
        if k in self.keys():            
            return getattr(self, k)
        return default
        
    def set(self, k, v):
        if k in ('html_field','file_object','dir_path','orig_name','guid_name',
                 'file_size','file_date','mime_type','file_ext','zip_size'):            
            setattr(self, k, v)
    
    def keys(self):
        for k in  ('html_field','file_object','dir_path','orig_name','guid_name',
                   'file_size','file_date','mime_type','file_ext','zip_size',
                   'file_name','zip_name','thumb_name','file_path','zip_path',
                   'thumb_path'):
            yield k
    
    def values(self):
        for k in self.keys():
            yield getattr(self, k)
        
    def items(self):
        for k in self.keys():
            yield (k, getattr(self, k))
    
    iterkeys = keys
    itervalues = values
    iteritems = items


class ExistingFileInfo(BaseFileInfo):
    """ returns info about an existing file """
    def __init__(self, file_path):
        self.dir_path, self.orig_name = os.path.split(file_path)
        self.guid_name = self._guess_name()
        if os.path.isfile(file_path):
            self.file_size = os.path.getsize(file_path)
            self.file_date = os.path.getctime(file_path)
        self.mime_type = self._guess_mimetype()
        self.file_ext = self._guess_extension().lower()


class ReusedFileInfo(BaseFileInfo):
    """ signals a reused file, no subsequent processing is required """
    def __init__(self, f):
        assert isinstance(f, BaseFileInfo), \
            'Argument must be of BaseFileInfo type, not %s' % type(f)
        for k in ('html_field','file_object','dir_path','orig_name','guid_name',
                  'file_size','file_date','mime_type','file_ext','zip_size'):
            setattr(self, k, getattr(f, k))


class UploadedFileInfo(BaseFileInfo):
    """ creates/returns info about an uploaded cgi.FieldStorage like file """
    def __init__(self, f, dir_path):        
        self.html_field = f.name
        self.file_object = f.file        
        self.dir_path = dir_path               
        self.orig_name = os.path.split(f.filename)[1]
        self.guid_name = str(uuid4()).replace('-','')                
        self.file_size = self._get_size(StreamIterator(f.file))
        self.file_date = datetime.utcnow()
        self.mime_type = self._guess_mimetype()
        self.file_ext = self._guess_extension().lower()
        self.zip_size = None

    def _get_size(self, f):
        s = 0 
        for d in f:
            s += len(d)
        return int(s)         




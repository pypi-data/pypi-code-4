#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import logging
log = logging.getLogger(__name__)

__all__ = ('StreamIterator',)

class StreamIterator(object):    
    def __init__(self, stream, chunk=8192):
        self.stream = stream
        self.chunk = chunk
        
        if hasattr(self.stream, 'open'):
            self.stream.open()
                
        if hasattr(self.stream, 'seek'):
            try:
                #e.g. zipfile.ZipExtFile has a seek() method but is not seekable
                if hasattr(self.stream, 'seekable'): 
                    if self.stream.seekable():                
                        self.stream.seek(0)
                else:
                    self.stream.seek(0)
            except Exception as e:
                log.error(e)
                
    def __iter__(self):
        return self    
    
    def __next__(self):
        data = self.stream.read(self.chunk)
        if data:
            return data
        raise StopIteration()
        
    def next(self):
        data = self.stream.read(self.chunk)
        if data:
            return data
        raise StopIteration()
        
    def close(self):
        if hasattr(self.stream, 'close'):
            self.stream.close() 
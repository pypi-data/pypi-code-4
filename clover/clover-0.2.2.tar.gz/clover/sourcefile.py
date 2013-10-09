from __future__ import absolute_import
import os
import time
import logging

logger = logging.getLogger('clover.SourceFile')
logger.setLevel(logging.DEBUG)


class SourceFile(object):
    path = None
    precompile = False
    requires = None
    _cached_code_time = None
    _cached_code = None
    
    def __init__(self, path=None):
        self.path = os.path.abspath(path)
        self.requires = set()

    def check_exists(self):
        return os.path.exists(self.path)

    def is_cache_expired(self):
        """ Returns True if the cached code time < modified time. 
        """

        if not os.path.exists(self.path):
            raise Exception("Cant check expiration of removed file.")

        if self.cached_code is None:
            return True

        return self.get_modified_time() > self._cached_code_time

    @property
    def cached_code(self):
        """ Code cached in memory. Setting this value updates the cached code time. 
        """
        return self._cached_code

    @cached_code.setter
    def cached_code(self, value):
        self._cached_code_time = time.time()
        self._cached_code = value

    def get_code_cached(self):
        """ Return the code from the cache. 
        """
        if self.is_cache_expired():
            logger.debug('Cache expired or empty. %s', self.path)
            self.cached_code = self.get_code()

        return self.cached_code

    def get_code(self):
        """ Return the original code. 
        """
        return open(self.path, 'r').read()

    def get_modified_time(self):
        """ Return the time the source was modified. 
        """
        # the maxiumum modification time (of the file, or related to the inode)
        return max(os.path.getmtime(self.path), os.path.getctime(self.path))

    def get_provide_names(self):
        """ Get list of names providing. """
        raise NotImplementedError

    def get_require_names(self):
        """ Get list of names requiring. """
        raise NotImplementedError

    def __repr__(self):
        return "SourceFile(%s)" % (self.path)

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self.__eq__(other)


def get_requirements_from_sourcefiles(sources):
    requirements = set()
    for source in sources:
        map(requirements.add, source.get_require_names())
        
    return requirements
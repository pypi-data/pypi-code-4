import logging
import json

__author__ = 'nate'


class OutputManifest(object):
    # TODO: cleanup outputs once read
    _source = None
    _source_map = None
    _externs = None

    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.data = json.loads(f.read())
            logging.debug('Read output manifest %s', self.data)

    @property
    def source(self):
        #return self.data['source']
        if self._source is None and 'source' in self.data:
            self._source = open(self.data['source']).read()
        return self._source

    def wrap_source(self, wrapper=None):
        if wrapper:
            return wrapper.encode('utf-8') % self.source

        return self.source

    @property
    def source_map(self):
        #return self.data['source-map']
        if self._source_map is None and 'source-map' in self.data:
            self._source_map = open(self.data['source-map']).read()
        return self._source_map


    @property
    def externs(self):
        #return self.data['externs']
        if self._externs is None and 'externs' in self.data:
            self._externs = open(self.data['externs']).read()
        return self._externs


    @property
    def errors(self):
        return self.data.get('errors', [])


    @property
    def warnings(self):
        return self.data.get('warnings', [])

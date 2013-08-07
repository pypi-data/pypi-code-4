from __future__ import absolute_import
import logging
import time
import os
from clover.config.cloverconfig import CloverConfig
from clover.config.markedloader import marked_load

class YamlConfig(CloverConfig):
    last_parse = None
    data = None

    def __init__(self, filename):
        super(YamlConfig, self).__init__()
        self.filename = os.path.abspath(os.path.expanduser(filename))
        if not os.path.exists(self.filename):
            raise Exception("Configuration file does not exist.")
        #self.parse(open(self.filename).read())


    @property
    def dirty(self):
        if self.last_parse is None:
            return True

        if os.path.getmtime(self.filename) > self.last_parse:
            return True

        return False

    def parse(self, data):
        #data = open(self.filename, 'r').read()
        self.data = marked_load(data)
        self.last_parse = time.time()
        
        
    @classmethod
    def from_file(cls, filename):
        logging.info('Loading yaml config %s', filename)
        c = cls(filename)
        c.parse(open(filename).read())
        return c
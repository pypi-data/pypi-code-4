from __future__ import absolute_import
import logging
import time
import os
from clover.config.cloverconfig import CloverConfig
from clover.config.markedloader import marked_load_all


class MultiDocConfig(object):
    last_parse = None
    data = None

    def __init__(self, filename):
        self.filename = filename
        self.configs = {}
        
    def add_config(self, config):
        self.configs[config.get_id()] = config
        

    def get_configs(self):
        return self.configs.values()

    def parse(self, data):
        self.data = marked_load_all(data)
        self.last_parse = time.time()
        

        # make a map of id -> config
        for config in self.data:
            config_id = config.get('id')

            if config_id is None:
                raise Exception("Missing config id")

            c = CloverConfig()
            c.filename = self.filename
            c.data = config
            self.add_config(c)


        logging.info('Resolve config parents: %s', self.configs)

        # resolve config parents
        for config in self.configs.values():
            config_id = config.get('id')
            next_config_id = config.read_option(config.options.inherits)
            while next_config_id:
                if next_config_id not in self.configs:
                    raise Exception("config '%s' to inherit doesnt exist." % next_config_id)

                parent = self.configs.get(next_config_id)
                config.parents.append(parent)
                next_config_id = parent.read_option(parent.options.inherits)
                if next_config_id == config_id:
                    raise Exception("A config cant include itself.")


    def get_config(self, id):
        if self.last_parse < os.path.getmtime(self.filename):
            logging.debug('Configuration has changed. Reloading.')
            with open(self.filename) as f:
                self.parse(f.read())
        
        return self.configs.get(id)
    
    @classmethod
    def from_file(cls, filename):
        config = cls(filename)
        with open(filename) as f:
            config.parse(f.read())
        return config
        
    
    

import unittest


TEST_MULTIDDOC = '''\
---
id: a
debug: False
paths:
- src
---
id: b
inherits: a
debug: True
'''


class TestMultiConfig(unittest.TestCase):
    def test(self):
        mdc = MultiDocConfig('.')
        mdc.parse(TEST_MULTIDDOC)

        config_a = mdc.get_config('a')
        config_b = mdc.get_config('b')
        print config_b.read_option(config_b.options.paths)
        print config_a.read_option(config_b.options.paths)

        self.fail(True)
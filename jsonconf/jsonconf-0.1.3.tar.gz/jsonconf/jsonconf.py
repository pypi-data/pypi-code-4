#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
from collections import MutableMapping
import os
import re
import simplejson as json

JSON_EXT = 'json'


class JSONConf(MutableMapping):
    '''
        Config object using json as its underlying data store

        Provides helper-methods for setting and saving
        options and config object properties
    '''
    def __init__(self, config_file, config_dir, default=None,
                 autosave=False, force=False):
        if not config_file:
            raise ValueError("No config file defined")
        elif isinstance(config_file, JSONConf):
            config_file = config_file.config_file
        elif isinstance(config_file, basestring):
            if not re.search('%s$' % JSON_EXT, config_file, re.I):
                config_file = '.'.join((config_file, JSON_EXT))
            else:
                config_file = os.path.expanduser(config_file)
        else:
            raise TypeError(
                "Unknown config_file type; got: %s" % type(config_file))

        self.config_dir = config_dir
        self.config_file = config_file
        self.autosave = autosave
        self.force = force

        self._set_dir_path()
        self._set_default_config(default)
        self._set_path()
        self._load()

    def _set_dir_path(self):
        if not self.config_dir:
            raise ValueError("config_dir is not set")
        else:
            config_dir = os.path.expanduser(self.config_dir)
        self._dir_path = config_dir

    def _set_default_config(self, default):
        if default and isinstance(default, dict):
            self.config = default
        elif default and isinstance(default, JSONConf):
            self.config = default.config
        else:
            self.config = {}

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value
        if self.autosave:
            self.save()

    def __delitem__(self, key):
        del self.config[key]

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)

    def __repr__(self):
        return repr(self.config)

    def __str__(self):
        return str(self.config)

    def __hash__(self):
        return hash(tuple(sorted(self.config.items())))

    def setdefault(self, key, value):
        self.config.setdefault(key, value)

    def values(self):
        return self.config.values()

    def _set_path(self):
        '''
            set config object's internal path to where
            config data will be stored/retrieved
        '''
        if os.path.exists(self.config_path):
            pass
        elif self.force:
            if not os.path.exists(self.dir_path):
                logger.warn('mkdirs (%s)' % self.dir_path)
                os.makedirs(self.dir_path)
            logger.warn('Write empty config (%s)' % self.config_path)
            # init an empty json dict at path
            write_empty_json_dict(self.config_path)
        else:
            raise IOError("Failed to load config: %s" % self.config_path)
        self.path = self.config_path

    def _load(self):
        ''' load config data from disk '''
        with open(self.path, 'r') as config_file:
            self.config.update(json.load(config_file))

    def save(self):
        ''' save config data to disk '''
        with open(self.path, 'w') as config_file:
            config_string = json.dumps(self.config, indent=2)
            config_file.write(config_string)

    def setup_basic(self, option, prompter):
        '''
            Helper-Method for getting user input with prompt text
            and saving the result
        '''
        x_opt = self.config.get(option)
        print '\n(Press ENTER to use current: %s)' % x_opt
        n_opt = prompter()
        if n_opt:
            self.config[option] = n_opt
            logger.debug('Updated Config: \n%s' % self.config)
        return n_opt

    def _property_default(self, option, default):
        ''' Helper-Method for setting config property, with default '''
        try:
            self._properties[option]
        except KeyError:
            self._properties[option] = default
        return self._properties[option]

    def _default(self, option, default=None, required=False):
        ''' Helper-Method for setting config argument, with default '''
        try:
            self.config[option]
        except KeyError:
            if default is None and required:
                raise ValueError(
                    "%s attribute is not set (required)" % option)
            else:
                self.config[option] = default
        return self.config[option]

    @staticmethod
    def yes_no_prompt(question, default='yes'):
        ''' Helper-Function for getting Y/N response from user '''
        # FIXME: make this as regex...
        valid_yes = ["Y", "y", "Yes", "yes", "YES", "ye", "Ye", "YE"]
        valid_no = ["N", "n", "No", "no", "NO"]
        if default == 'yes':
            valid_yes.append('')
        else:
            valid_no.append('')
        valid = valid_yes + valid_no
        prompt = '[Y/n]' if (default == 'yes') else '[y/N]'
        ans = raw_input('%s %s ' % (question, prompt))
        while ans not in valid:
            print 'Invalid selection.'
            ans = raw_input("%s " % prompt)
        return ans in valid_yes

    def _json_bool(self, value):
        '''
            Helper-Function for converting various forms
            of bool to a json compatible form
        '''
        if value in [0, 1]:
            return value
        elif value is True:
            return 1
        elif value is False:
            return 0
        else:
            raise TypeError('expected 0/1 or True/False')

    @property
    def dir_path(self):
        return os.path.expanduser(self._dir_path)

    @property
    def config_path(self):
        return os.path.join(self.dir_path, self.config_file)


def write_empty_json_dict(fname):
    with open(fname, 'a') as f:
        f.write('{}')


def test_write_empty_json_dict():
    from random import random
    random_filename = 'test_empty_dict.%s' % random()
    path = os.path.join('/tmp/', random_filename)
    write_empty_json_dict(path)
    with open(path) as f:
        empty_dct = json.load(f)
        assert empty_dct == {}

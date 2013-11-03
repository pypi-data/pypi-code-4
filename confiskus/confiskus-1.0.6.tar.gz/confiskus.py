# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 beezz <beezz@T500>


import os
import ConfigParser


def _get_defaults(conf_filename):
    return {
        'env.file_dir': os.path.abspath(os.path.dirname(conf_filename)),
        'env.working_dir': os.path.abspath(os.getcwd()),
    }


class Confiskus(object):

    def __init__(
        self,
        defaults=None,
        parents=None,
        use_env=True,
        config_instance=None,
        parser_class=ConfigParser.SafeConfigParser,
    ):
        self.parents = [] if parents is None else parents
        self.defaults = {} if defaults is None else defaults
        self.ParserClass = parser_class
        self.use_env = use_env
        self.config_instance = config_instance

    def _get_defaults(self, fn):
        defaults = {}
        if self.use_env:
            defaults.update(_get_defaults(fn))
        defaults.update(self.defaults)
        return defaults

    def _get_parent(self, fn):
        cnf = ConfigParser.SafeConfigParser(defaults=self._get_defaults(fn))
        cnf.read(fn)
        return cnf.get('default', 'extends')

    def build_parents(self, fn, parents):
        try:
            parent = self._get_parent(fn)
            self.build_parents(fn=parent, parents=parents)
            parents.append(parent)
        except (
            ConfigParser.NoSectionError,
            ConfigParser.NoOptionError,
        ):
            pass

    def read(self, filenames):
        if isinstance(filenames, basestring):
            filenames = [filenames, ]
        all_files = self.parents[:]
        for fn in filenames:
            self.build_parents(fn=fn, parents=all_files)
            all_files.append(fn)
        config = self.config_instance
        if config is None:
            config = self.ParserClass(
                defaults=self._get_defaults(all_files[-1]),
            )
        config.read(all_files)
        return config

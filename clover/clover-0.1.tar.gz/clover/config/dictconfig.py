import logging
import os
from clover.config.baseconfig import BaseConfig


class DictConfig(BaseConfig):
    filename = None

    def __init__(self):
        super(DictConfig, self).__init__()
        self.data = {}
        self.parents = []

    @property
    def dirty(self):
        return True

    @property
    def basedir(self):
        return os.path.dirname(self.filename)

    def has_option(self, item):
        has_option = item in self.data
        # check parents for the option
        if self.parents and not has_option:
            parents_have_option = False
            for parent in self.parents:
                if parent.has_option(item):
                    parents_have_option = True
            return parents_have_option
        return has_option

    def get(self, *args):
        item = args[0]
        default_value = None if len(args) == 1 else args[1]

        has_option = item in self.data
        # check parents for the option
        if not has_option:
            logging.debug('Option missing %s', item)
            if self.parents:
                logging.debug('Checking parents for value %s: %s', item, self.parents)
                for parent in self.parents:
                    if parent.has_option(item):
                        return parent.get(item)
            return default_value
        return self.data.get(*args)
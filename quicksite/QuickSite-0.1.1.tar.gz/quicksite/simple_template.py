""" A simple template that is rendered using the data provided in the config file. """


__author__ = "Russell Hay"

import logging
log = logging.getLogger(__name__)

import os
import os.path as path

import quicksite.helper

class SimpleTemplate(object):
    def __init__(self, destination, source):
        self._source = source
        self._destination = destination

    def __call__(self, env, output_dir, data):
        template = env.get_template(self._source)
        output = template.render(**data)
        output_file = path.join(output_dir, self._destination)
        quicksite.helper.ensure_directory(output_file)
        log.info("Generating {1}->{0}".format(self._destination, self._source))
        with open(output_file, "w") as f:
            f.write(output)

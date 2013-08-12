""" TODO: Describe File
"""

__author__ = "Russell Hay"

import logging
log = logging.getLogger(__name__)

import os
import os.path as path

import quicksite.helper
import quicksite.template_factory

class MultiTemplate(object):
    def __init__(self, destination_template, definition):
        self._destination_template = destination_template
        self._key = definition['data_name']
        self._source = definition['template']

    def __call__(self, env, output_dir, data):

        template = env.get_template(self._source)
        for item in data[self._key]:

            self._generate_template(template, output_dir, item)

    def _generate_template(self, template, output_dir, data):
        output = template.render(**data)

        output_path = self._expand_path(data)
        output_file = path.join(
            output_dir,
            output_path
        )
        log.info("Generating {0} -> {1}".format(self._source, output_path))
        quicksite.helper.ensure_directory(output_file)

        with open(output_file, "w") as f:
            f.write(output)

    def _expand_path(self, data):
        real_data = dict(filter(
            lambda x: "{{{0}}}".format(x[0]) in self._destination_template,
            data.items()
        ))

        return self._destination_template.format(**real_data)

quicksite.template_factory.register_template("multi", MultiTemplate)

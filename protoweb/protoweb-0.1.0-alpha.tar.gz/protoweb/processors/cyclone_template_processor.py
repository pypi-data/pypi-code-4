# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

import os

import cyclone.escape
import cyclone.template

from protoweb.fs import read_file
from protoweb.processors import Processor


class CycloneTemplateProcessor(Processor):

    id_ = 'cyclone_tpl'

    def match(self, filename):
        return self.argument_map.get('tpl') in ['1', 'true', 'yes']

    def process(self, filename):

        json = os.path.basename(filename)
        json = json[:json.rfind('.') + 1] + 'json'
        json = os.path.abspath(
            os.path.join(self.handler.config['options'].json_path, json)
        )

        data = None
        if os.path.isfile(json):
            data = cyclone.escape.json_decode(read_file(json))
        loader = cyclone.template.Loader(os.path.dirname(filename))
        return dict(
            content=loader.load(os.path.basename(filename)).generate(data=data),
            headers=[
                ('Content-Type', 'text/html')
            ]
        )

# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

import subprocess

import protoweb.util
from protoweb.processors import Processor


class LessProcessor(Processor):

    id_ = 'less'

    def __init__(self, handler, argument_map):
        self.handler = handler
        self.argument_map = argument_map
        self.lessc = protoweb.util.which('lessc')

    def match(self, filename):
        return filename.endswith('.less')

    def process(self, filename):
        if self.lessc is None:
            return super(LessProcessor, self).process(filename)
        comp = [self.lessc]
        if self.handler.config['options'].less_flags:
            comp += map(lambda x: "--%s" % x,
                        self.handler.config['options'].less_flags)
        comp.append(filename)
        css = subprocess.check_output(comp)
        return dict(
            content=css,
            headers=[
                ('Content-Type', 'text/css')
            ]
        )

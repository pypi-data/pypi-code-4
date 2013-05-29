# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

import mimetypes

from protoweb.fs import read_file


class Processor(object):

    _id = 'default_processor'
    name = classmethod(lambda cls: cls._id)

    def __init__(self, handler, argument_map):
        self.handler = handler
        self.argument_map = argument_map

    def match(self, filename):
        return True

    def process(self, filename):
        m = mimetypes.guess_type(filename, False)
        if m is not None:
            flag = 'rb' if m[0].startswith('image') else 'r'
            return dict(
                content=read_file(filename, flag),
                headers=[
                    ('Content-Type', m[0])
                ]
            )
        else:
            return dict(content=read_file(filename))

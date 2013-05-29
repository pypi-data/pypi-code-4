# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

import os
import traceback

import cyclone.web
import cyclone.escape

_e = lambda s: cyclone.escape.xhtml_escape(s)


class ProcessorHandler(cyclone.web.RequestHandler):

    _processors = []

    @classmethod
    def add_processor(cls, processor):
        if processor not in cls._processors:
            cls._processors.append(processor)

    @classmethod
    def get_processors(cls):
        return cls._processors

    def write_error(self, status_code, **kw):
        self.write('<h1>OK, an error %i occurred!</h1>' % status_code)
        self.write('<pre>')
        for k in kw:
            if k == 'traceback':
                self.write('<li><b>%s</b><br/><pre>%s</pre></li>' % (_e(k), _e(kw[k])))
                continue
            self.write('<li><b>%s:</b> %s</li>' % (_e(k), _e(kw[k])))
        self.write('</pre>')

    def initialize(self, **kw):
        self.config = kw

    def get(self, path):

        if self.config.get('hide-favicon', True) and 'favicon' in path:
            return

        o = path
        # get rid of first slash, if any
        if path.startswith('/'):
            path = path[1:]

        if not path:
            path = self.config.get('root-index', 'html/index.html')

        argmap = dict(map(lambda k: (k, self.get_argument(k)),
                          self.request.arguments.keys()))

        headers = [('Cache-Control', 'no-cache, no-store')]
        content = ''

        if not self.get_processors():
            self.send_error(500, message='there is no processors registered')
            return

        try:

            for src in self.config['options'].sources:
                f = os.path.abspath(os.path.join(src, path))
                if os.path.isfile(f):
                    path = f
                    break

            for processor in self.get_processors():
                p = processor(self, argmap)
                if p.match(o):
                    result = p.process(path)
                    if result.get('headers'):
                        headers += result.get('headers')
                    if result.get('content'):
                        content = result.get('content')
                    break

            for header in headers:
                self.set_header(*header)

            if content:
                self.write(content)
            else:
                self.send_error(
                    500,
                    message='please see your log, request path was: %s' % o
                )

        except Exception, e:
            self.send_error(
                500,
                message='please see your log, request path was: %s' % o,
                exception_msg=e.message,
                traceback=traceback.format_exc()
            )

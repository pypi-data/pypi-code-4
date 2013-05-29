# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

from __future__ import absolute_import

import uuid
import cyclone.web

from .handler import ProcessorHandler


class ProtoWebServer(cyclone.web.Application):

    def __init__(self, options):

        self.port = options.port
        self.interface = options.interface

        settings = dict(
            cookie_secret=str(uuid.uuid4()),
            xsrf_cookies=False,
            debug=True
        )

        handlers = [
            (r"(.*)", ProcessorHandler, dict(options=options))
        ]

        cyclone.web.Application.__init__(self, handlers, **settings)

    def run(self):
        import sys
        from twisted.internet import reactor
        from twisted.python import log

        log.startLogging(sys.stdout)
        reactor.listenTCP(self.port, self, interface=self.interface)
        reactor.run()

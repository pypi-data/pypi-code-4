from __future__ import absolute_import
import argparse
import logging

import os
import webapp2
from cherrypy import wsgiserver

from clover.config.multiconfig import MultiDocConfig
from clover.server.reloader import install
from clover.service import Service


routes = [
    webapp2.Route('/', 'clover.server.handlers.index.Index', 'index'),
    webapp2.Route('/library/<path:.+>', 'clover.server.handlers.library.Handler',
                  'library'),
    webapp2.Route('/configs/<id>/deps.js', 'clover.server.handlers.deps.Handler', 'deps'),
    webapp2.Route('/configs/<id>/externs.js', 'clover.server.handlers.externs.Handler',
                  'externs'),
    webapp2.Route('/configs/<id>/input<path:.+>', 'clover.server.handlers.input.Handler',
                  'input'),
    webapp2.Route('/configs/<id>/output.js', 'clover.server.handlers.compile.Handler',
                  'compile'),
    webapp2.Route('/configs/<id>/precompile<path:.+>',
                  'clover.server.handlers.precompile.Handler', 'precompile'),
    webapp2.Route('/configs/<id>/sourcemap', 'clover.server.handlers.sourcemap.Handler',
                  'sourcemap'),
    webapp2.Route('/configs/<id>/sources', 'clover.server.handlers.listsources.Handler',
                  'list-sources'),
    webapp2.Route('/configs/<id>/tests', 'clover.server.handlers.listtests.Handler',
                  'list-tests'),
    
    webapp2.Route('/configs/<id>/testcommand', 'clover.server.handlers.testcommand.Handler', 'test-command'),
    webapp2.Route('/configs/<id>/testrunner', 'clover.server.handlers.testrunner.Handler',
                  'test-runner'),
    webapp2.Route('/configs/<id>/test<path:.+>', 'clover.server.handlers.test.Handler', 'test')
]

class Server(object):
    def __init__(self, mdc):
        self.mdc = mdc

    install_watch_thread = False
    
    address = '127.0.0.1'
    port = 2323

    def set_port(self, p):
        self.port = p
        
    def set_address(self, address):
        self.address = address

    def start(self):
        logging.info('Starting server')

        Service.start()

        mdc = self.mdc

        c = {
           'config': mdc,
           'port': self.port,
           'address': self.address 
        }
        
        app = webapp2.WSGIApplication(routes=routes, debug=True, config=c)
        

        if self.install_watch_thread:
            # start a thread to watch paths for js/soy modifications
            install(4, [self.mdc.filename])

        server = wsgiserver.CherryPyWSGIServer((self.address, self.port), app)

        try:
            server.start()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()


def main(args=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('config')
    args = argparser.parse_args(args)

    configfile = os.path.abspath(os.path.expanduser(args.config))
    mdc = MultiDocConfig(configfile)
    mdc.parse(open(configfile).read())

    s = Server(mdc)
    s.install_watch_thread = False
    s.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
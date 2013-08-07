from __future__ import absolute_import
import sys
import argparse
import os
from clover.command import Command
from clover.config.multiconfig import MultiDocConfig
from clover.server.main import Server

argparser = argparse.ArgumentParser()
argparser.add_argument('config')
argparser.add_argument('-a', '--address', default="127.0.0.1")
argparser.add_argument('-p', '--port', default=2323)

class Serve(Command):
    def start(self, args):

        
        
        #argparser = argparse.ArgumentParser()
        #argparser.add_argument('config')
        args = argparser.parse_args(args)
    
        configfile = os.path.abspath(os.path.expanduser(args.config))
        mdc = MultiDocConfig(configfile)
        mdc.parse(open(configfile).read())
    
        s = Server(mdc)
        s.install_watch_thread = False
        s.start()
        #main(args)
    
    
if __name__ == '__main__':
    Serve.run(sys.argv[1:])
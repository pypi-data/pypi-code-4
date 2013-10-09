from __future__ import absolute_import
import logging
import argparse
import clover
import sys

argparser = argparse.ArgumentParser()
argparser.add_argument('command')
argparser.add_argument('remainder', nargs=argparse.REMAINDER)
argparser.add_argument('-d','--debug', default=False, action="store_true")
argparser.add_argument('-v','--verbose', default=False, action="store_true")

def main(args=None):
    parsed_args = argparser.parse_args(args)
    
    
    level = logging.ERROR
    
    if parsed_args.verbose:
        level = logging.INFO
        
    if parsed_args.debug:
        level = logging.DEBUG
        
    logging.basicConfig(level=level)    
    
    if parsed_args.command == "build":
       import clover.commands.build
       cmd = clover.commands.build.Build
    elif parsed_args.command == "serve":
        import clover.commands.serve
        cmd = clover.commands.serve.Serve
    elif parsed_args.command == "messages":
        import clover.commands.messages
        cmd = clover.commands.messages.Messages
    elif parsed_args.command == "convertpo":
        import clover.commands.convertpo
        cmd = clover.commands.convertpo.ConvertPO
    elif parsed_args.command == "test":
        import clover.commands.test
        cmd = clover.commands.test.Test
    else:
        print "Invalid command:", parsed_args.command
        sys.exit(-1)
    cmd.run(parsed_args.remainder)
    


if __name__ == '__main__':
    main()
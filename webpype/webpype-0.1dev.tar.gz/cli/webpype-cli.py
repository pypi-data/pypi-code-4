#!/usr/bin/env python
from __future__ import print_function
import argparse
import sys

from webpype import WebPypeClient

parser = argparse.ArgumentPatser(description='''WebPype -- Python CLI tool for
                                 WebPipes.''')

parser.add_argument('-v', '--version', action='version',
                   version='WebPype-CLI v0.1')

parser.add_argument('-u', '--url', dest='url',
                    help='''The URL for the 
                    WebPipe you want to use.''',
                    required=True)

cmd_type = parser.add_mutually_exclusive_group()
cmd_type.add_argument('-r', '--raw_input', dest='raw_input',
                      help='For raw input.')
#cmd_type.add_argument('-f', '--file', dest='file',
#                      help='Path to a file, use that file as input')
cmd_type.add_argument('-o', '--options', dest='options',
                      help='''If you want to see the OPTIONS
                      from a specific WebPipe''')

args = parser.parse_args()

if __name__ == '__main__':
    url = args.url
    webpipe = WebPypeClient()

    if not args.options:
        if args.raw_input:
            input = args.raw_input
    else:
        print(webpipe.options(url))

#!/usr/bin/env python

import argparse


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('--spam', help=argparse.SUPPRESS)
parser.add_argument('--' + 'eggs' * 20, dest='eggs')
parser.print_usage()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Phil Adams http://philadams.net

clc: simple charts on the command line.
http://github.com/philadams/clc
"""

import logging
import sys


def cli():
    import argparse

    # populate and parse command line options
    description = 'clc: simple charts on the command line.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--width', '-w', default=50, type=int)
    parser.add_argument('--tick', '-t', default=u'▇')
    parser.add_argument('infile', nargs='?', default=sys.stdin,
            type=argparse.FileType('rU'), help='data file (or stdin)')
    args = parser.parse_args()

    # logging config
    log_level = logging.WARNING  # default
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    logging.debug('args: %s' % args.__repr__())

    # read data
    labels, data = [], []
    for line in args.infile.readlines():
        if line.strip() == '':
            continue
        label, datum = line.strip().split(' ')
        labels.append(label)
        data.append(int(datum))

    # massage data
    labels_width = max(map(len, labels))
    width = args.width - labels_width - 1 - 4
    step = max(data) / float(width)
    blocks = [int(d / step) for d in data]

    # output command line chart
    for i, label in enumerate(labels):
        lbl = '%s ' % (label.rjust(labels_width, ' '))
        sys.stdout.write('%s ' % lbl)
        if blocks[i] < step:
            pass
            #sys.stdout.write('|')
        else:
            sys.stdout.write(args.tick * blocks[i])
        sys.stdout.write('  %d' % data[i])
        sys.stdout.write('\n')


if '__main__' == __name__:
    cli()

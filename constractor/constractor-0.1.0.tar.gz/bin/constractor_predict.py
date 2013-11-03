#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013, David Kuryakin (dkuryakin@gmail.com)
#
# This material is provided "as is", with absolutely no warranty expressed
# or implied. Any use is at your own risk.
#
# Permission to use or copy this software for any purpose is hereby granted
# without fee. Permission to modify the code and to distribute modified
# code is also granted without any restrictions.

from constractor.parser import Parser
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser(usage='Usage: %prog [options] arguments')
    parser.add_option("-m", "--model", dest="model",
        help="file with dumped model", metavar="MODEL_FILE")
    parser.add_option("-u", "--url", dest="url",
        help="target url to parse and predict", metavar="URL")
    parser.add_option("-o", "--output", dest="output",
        help="file with results", metavar="FILE")

    options, args = parser.parse_args()
    if not options.model:
        parser.error('Specify model file with -m option!')
    if not options.url:
        parser.error('Specify url with -u option!')
    if not options.output:
        parser.error('Specify output file with -o option!')

    predicted = Parser(options.url, model_file=options.model).predicted
    for i, element in enumerate(predicted):
        with open(options.output + '.' + str(i), 'w') as f:
            print >> f, unicode(element.toInnerXml()).encode('utf-8')

#!/usr/bin/python
'''
reduce bit depth of 16 bit images to 8 bit
'''

import chameleon, numpy, os, time, sys, util

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'image'))
import CUAVScanner

from optparse import OptionParser
parser = OptionParser("reduce_depth.py [options] <filename..>")
parser.add_option("--output", default='raw8', help="output directory")
(opts, args) = parser.parse_args()

def process(files):
  '''process a set of files'''

  count = 0
  for f in files:
    pgm = util.PGM(f)
    im = pgm.array
    im_8bit = numpy.zeros((960,1280,1),dtype='uint8')
    scanner.reduce_depth(im, im_8bit)
    newname = os.path.join(opts.output, os.path.basename(f))
    print('%s -> %s [%u/%u]' % (f, newname, count, len(files)))
    count += 1
    chameleon.save_pgm(newname, im_8bit)

process(args)

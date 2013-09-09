"""
Renormalise a set of images from the command line to the full [0, 255] range
and save as a set of PNG files.

Usage:
    renormimg [options] [<IMAGE>...]

Options:
    -h, --help                  Show brief usage summary.
    -v, --verbose               Be more verbose in logging.
    -s SUFFIX, --suffix=SUFFIX  Suffix to append to converted files.
                                [default: .renorm.png]

"""

import logging
import sys

from docopt import docopt
import numpy as np
from matplotlib.pyplot import imread, imsave, cm

def main():
    opts = docopt(__doc__)
    if opts['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARN)

    logging.info('Using filename suffix: {0}'.format(opts['--suffix']))

    if len(opts['<IMAGE>']) == 0:
        logging.info('No images specified. Exiting successfully.')
        sys.exit(0)

    logging.info('Pre-scanning images...')

    min_val, max_val = np.inf, -np.inf
    for filename in opts['<IMAGE>']:
        logging.info('Scanning {0}'.format(filename))
        A = imread(filename)
        max_val = max(np.max(A), max_val)
        min_val = min(np.min(A), min_val)

    logging.info('Input images have values on interval [{0}, {1}].'.format(min_val, max_val))
    if max_val == min_val:
        logging.error('Images all have the same value pixels. Rescaling is meaningless.')
        sys.exit(1)

    for filename in opts['<IMAGE>']:
        out_filename = filename + opts['--suffix']
        logging.info('Re-scaling {0} to {1}'.format(filename, out_filename))
        A = np.array(imread(filename), dtype=np.float32)
        A -= min_val
        A /= max_val - min_val

        if len(A.shape) == 2:
            A = cm.gray(A)
        
        imsave(out_filename, A, format='png')

    logging.info('Finished')

# vim:sw=4:sts=4:et

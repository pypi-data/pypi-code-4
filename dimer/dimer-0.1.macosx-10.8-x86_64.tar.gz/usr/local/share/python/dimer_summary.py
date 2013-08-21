#!/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""Summary of an archive contents. Support:
    + dataset
    - training info
    - weight info
    - input representation
"""

import sys, random, argparse, logging, pdb
from operator import itemgetter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dimer import archive

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        epilog="Olgert Denas (Taylor Lab)")
    parser.add_argument("input", type=archive.dset_path,
            help="Input file. " + archive.DSPEC_MSG)
    opt = parser.parse_args()


    with pd.get_store(archive.archname(opt.input)) as store:
        for d in ("X", "Y", "T"):
            key = "%s/%s" % (archive.basename(opt.input), d)
            if key in store:
                print key
                print str( store[key] )



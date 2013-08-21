#!/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""Produce pandas panel
(<nr. anchors> X <nr. of tracks> X <genome interval width>)
from feature overlap data.
Data is dumped on an HDF5 archive of the type

/<hdf_path>X   wide    (shape->[<# anchors>,<# tracks>,<width>])
/<hdf_path>Y   series  (shape->[<nr. of anchors>])

"""


import os
import sys
import logging
#import pdb
import argparse
from operator import itemgetter
from multiprocessing import Pool


import numpy as np
import pandas as pd


from dimer.genome import bedops, bed
from dimer import archive, data, ops

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

if __name__ != '__main__':
    log.error("this is a script do not import")
    sys.exit(1)


def is_file(path):
    "file type checker"

    if not os.path.isfile( path ):
        raise IOError("%s is not a file. pipes/symlinks won't work" % path)
    return os.path.abspath( path )


parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    epilog="Taylor Lab (odenas@emory.edu)")
parser.add_argument("anchors", type=is_file, help="Gene regions (>= BED6)")
parser.add_argument("input", nargs="+", type=is_file,
                    help="Input features ( >= BED4)")
parser.add_argument("output", type=archive.dset_path,
                    help="Output file. " + archive.DSPEC_MSG)
parser.add_argument("--feature_score", action='store_true', default=False,
                    help=("Record scores featuresas signal. In "
                          "this case input must be >= BED5"))
parser.add_argument("--bin", type=int, default=10, help="bin (sum) signal")
parser.add_argument("--par", type=int, default=1, help="parallelize")
parser.add_argument("--fit", action='store_true', default=False,
                    help="For each track. Fit signal in [0, 1]")
opt = parser.parse_args()


def makeOverlaps(mapf, anchorf=opt.anchors, bin=opt.bin, fit=opt.fit):
    """represent features over anchors ovelapps as an data matrix anchor X width"""

    Xlst = []
    for anchor, feat_str in bedops.bedmap(anchorf, mapf, onlyOverlapping=False):
        Xlst.append(bedops.overlap_as_array(bedops.parseBED(anchor),
                                            feat_str.split(";"), bin) )
    log.info("%s: kept %d anchors", os.path.basename(mapf), len(Xlst))
    # (anchors X width )
    X = np.array( Xlst )
    if fit:
        X = ( 1.0 + ops.fit(X) ) / 2.0
    log.info("(%s) %s (min=%.4f, max=%.4f)...",
             os.path.basename(mapf), str(X.shape), X.min(), X.max())
    return X


MAP = (opt.par > 1 and Pool(processes=opt.par).map or map)

## (tracks X anchors X width)
xsig = np.rollaxis( np.array( MAP(makeOverlaps, opt.input) ), 1, 0 )

Xitems = map(itemgetter(3), bed.BedReader(open(opt.anchors)))

Xmajor_axis = map(lambda n: os.path.splitext(n)[0],
                  map(os.path.basename, opt.input))

Xminor_axis = range(-opt.bin * xsig.shape[2] / 2, opt.bin * xsig.shape[2] / 2, opt.bin)

X = pd.Panel(xsig, items=Xitems, major_axis=Xmajor_axis,
             minor_axis=Xminor_axis)
Y = pd.Series(np.array(map(itemgetter(4), bed.BedReader(open(opt.anchors))),
              dtype=np.float64) )

logging.getLogger("dimer.data").setLevel(logging.DEBUG)
data.AnchorDataset(X, Y, None).dump(opt.output)

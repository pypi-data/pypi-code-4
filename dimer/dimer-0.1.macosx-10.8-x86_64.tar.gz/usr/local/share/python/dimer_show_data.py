#!/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""plot various views of the data"""


import sys, random, argparse, logging, pdb
import inspect
import pdb
from operator import itemgetter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dimer import archive



logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

def _mean(fpath, did, idx):
    pX = archive.load_object( fpath, "%s/%s" % (did, idx) )
    dT = archive.load_object( fpath, "%s/T" % did )
    N,T,W = pX.shape

    fX = pX.values.reshape( (N, -1) )
    mean_fx_r = pd.DataFrame( fX[dT["label_name"].values == "R" ].mean( axis = 0 ).reshape( T, W ), index = pX.major_axis, columns = pX.minor_axis ).T
    mean_fx_i = pd.DataFrame( fX[dT["label_name"].values == "I" ].mean( axis = 0 ).reshape( T, W ), index = pX.major_axis, columns = pX.minor_axis ).T

    for track in mean_fx_r:
        pd.DataFrame( {"%s: induced" % track : mean_fx_i[track], "%s repressed" % track : mean_fx_r[track]} ).plot()
        plt.show()


def rmean(fpath, did):
    _mean(fpath, did, "rawX" )


def mean(fpath, did):
    _mean(fpath, did, "X" )

def browse(fpath, did):
    dfX = archive.load_object( fpath, "%s/X" % did )
    dfT = archive.load_object( fpath, "%s/T" % did )

    for i, (gene, tracks) in enumerate( dfX.iteritems() ):
        c = 'green'
        if dfT["label_name"][i] == "R":
            c = 'red'
        tracks.T.plot(subplots = True, color = c)
        plt.show()
        if i > 10:
            break


plotting_f = dict( filter(lambda (n,f): inspect.isfunction(f) and n[0] != "_",
    inspect.getmembers( sys.modules[__name__] )) )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        epilog="Olgert Denas (Taylor Lab)")
    parser.add_argument("input", type=archive.dset_path,
            help="Input file. " + archive.DSPEC_MSG)
    parser.add_argument("boxplot", choices=plotting_f.keys(),
            help="what to plot")

    opt = parser.parse_args()


    plotting_f[opt.boxplot](archive.archname(opt.input),
                            archive.basename(opt.input))
    plt.show()



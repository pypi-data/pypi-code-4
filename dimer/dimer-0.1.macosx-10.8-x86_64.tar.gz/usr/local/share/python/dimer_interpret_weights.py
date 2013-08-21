#!/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""Train a convolutional neural net for classification"""

import sys, argparse, pdb
import logging

import numpy as np
rng = np.random.RandomState()
import pandas as pd
import matplotlib.pyplot as plt

from dimer.nnet import nccn
from dimer.archive import dset_path, DSPEC_MSG, this_train_name, get_target_dataset, join
from dimer.nnet.config_spec import ModelSpec, MtrainSpec, DataSpec

epsilon=0.00001


def modeltop_inv(M, output):
    """invert the output of the model for the MLP layers

    M: model
    output : row array representing a desired target"""

    Y = np.log(output / (1 - output))
    for i in (-1, -2):
        W = M[i].get_weights()[0]
        iW = np.linalg.pinv( W.T )
        X = np.dot( iW, Y.T ).T
        print np.max( np.abs( 1 / (1 + np.exp( np.dot( X, M[i].get_weights()[0] ) - Y ) ) ) )
        pdb.set_trace()
        Y = np.log( X / (1 - X) )
    return X

def unpool(x, p):
    """un pool the array by expanding its rows

    x: array of size r X c
    p: pool size (width)
    return : array of size r X c*p"""

    x_ = np.zeros( (x.shape[0], x.shape[1]*p) )

    for r in range(x.shape[0]):
        for c in range(x.shape[1]):
            x_[r, c*p:(c+1)*p] = x[r,c]
    return x_

def roll(X_, C):
    R = X_.shape[0] / C
    X = np.zeros( (R, X_.shape[1] + C - 1) )

    for c in range(X_.shape[1]):
        if c == 0:
            X[:,0:C-1] = X_[:,0].reshape( (R,C) )[:,0:C-1]
        X[:,c+C-1] = X_[:,c].reshape( (R,C) )[:,-1]
    return X


def cp_inv(layer, output):
    assert len(output.shape) == 1 or output.shape[0] == 1

    ## (K, FM=1, R, C) ==> (K, C)
    W_ = layer.get_weights()[0]
    (K, FM, R, C) = W_.shape
    Y = unpool( output.reshape( (K, -1) ), layer.pshape[1] )

    for k in range(K):
        iW = np.linalg.pinv( W_[k,0].reshape(1,-1) )
        Xtilde = np.dot( iW, Y[k:k+1] )
        if k == 0:
            X = roll( Xtilde, C )
        else:
            X += roll( Xtilde, C )
    return X


if __name__ != "__main__":
    print >>sys.stderr, "this is a script. cannot import"
    sys.exit(1)

parser = argparse.ArgumentParser(description=__doc__,
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        epilog="Olgert Denas (Taylor Lab)")
parser.add_argument("settings", type=str, help="Experiment file of settings.")
parser.add_argument("input", type=dset_path, help="Input data."+DSPEC_MSG)
parser.add_argument("trainid", type=str, help="Train id")
opt = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


ms, tr = map(lambda c: c._from_settings(opt.settings), (ModelSpec, MtrainSpec))
ds = DataSpec._from_archive(opt.input, 1, rng, 0.1, 0)

M = nccn.CnnModel((ms.nkerns, ms.rfield, ms.pool), ms.lreg_size,
        (tr.batch_size, 1, ds.tracks, ds.width),
        ds.labels, rng,
        xdtype=np.float, ydtype='int32')
M.load( "/".join( (opt.input, opt.trainid) ) )

X = cp_inv(M[-3], modeltop_inv( M, np.array( [[1-epsilon, epsilon]] ) ))
Xdf = pd.DataFrame( X.T, columns=ds.track_names )
Xdf.plot()
plt.show()




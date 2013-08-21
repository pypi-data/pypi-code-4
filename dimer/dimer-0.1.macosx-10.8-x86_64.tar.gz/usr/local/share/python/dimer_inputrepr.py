#!/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""Compute the representations of the input in all layers of a
trained convolutional neural net"""

import sys
import argparse
#import pdb
import logging

import numpy as np
rng = np.random.RandomState()
import pandas as pd
import theano

from dimer.archive import dset_path, DSPEC_MSG, \
    load_object, save_object, archname, basename
from dimer.data import AnchorDataset
from dimer.nnet import nccn
from dimer.nnet.config_spec import ModelSpec

logging.basicConfig(level=logging.INFO)
logging.getLogger("dimer.archive").setLevel(logging.DEBUG)
log = logging.getLogger()

if __name__ != "__main__":
    print >>sys.stderr, "this is a script. cannot import"
    sys.exit(1)

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    epilog="Olgert Denas (Taylor Lab)")
parser.add_argument("settings", type=str, help="Experiment file of settings.")
parser.add_argument("input", type=dset_path, help="Input data." + DSPEC_MSG)
parser.add_argument("trainid", type=str, help="Id of the train experiment")
parser.add_argument("--action", choices=("compute", "check"), default="compute",
                    help="Compute model states or check consistency.")
parser.add_argument("--raw", action='store_true', default=False,
                    help=("Use the raw version of the data."
                          "These are fitted in [0,1], but not normalized."))
opt = parser.parse_args()


def dump_state(archpath, layerpath, x, gene_names):
    if len( x.shape ) == 4:
        obj = pd.Panel(x.reshape((x.shape[0], x.shape[1], -1)),
                       items=gene_names)
    elif len(x.shape) == 2:
        obj = pd.DataFrame(x, index=gene_names)
    print obj
    save_object(archpath, layerpath, obj)


def state_path(i):
    return "/".join( (basename(opt.input), opt.trainid,
                      "layer_%d" % i, "state") )


def load_state(i):
    if i < 0:
        return ds.X
    return load_object( archname(opt.input), state_path(i) ).values

ms = ModelSpec._from_settings(opt.settings)
ds = AnchorDataset._from_archive( opt.input, opt.raw )

M = nccn.CnnModel(ms.cp_arch, ms.lreg_size,
                  (ds.X.shape[0], 1, ds.tracks, ds.width),
                  ds.labels, rng,
                  xdtype=ds.X.dtype, ydtype=str(ds.T.dtype))
M.load( "/".join( (opt.input, opt.trainid) ) )

act_f = {}
for i, layer in enumerate(M):
    log.info("compiling activation of layer %d ...", i)
    act_f[i] = theano.function( inputs=[layer.input], outputs=layer.activation() )

if opt.action == "compute":
    X = ds.X.reshape( (1, ds.X.shape[0], 1, ds.X.shape[1], ds.X.shape[2]) )
    x = X[0]
    ## for a model with 4 layers, you can thus do this
    ## act_f[3]( act_f[2]( act_f[1]( act_f[0]( x ) ).reshape((opt.batch_size, -1)) ) )

    # convpool layers
    for i in range(len(M))[:-2]:
        x = act_f[i]( x )
        dump_state(archname(opt.input), state_path(i), x, None)

    # fully connected layers
    x = x.reshape( (ds.X.shape[0], -1) )
    for i in range(len(M) - 2, len(M)):
        x = act_f[i]( x )
        dump_state(archname(opt.input), state_path(i), x, None)
else:
    assert opt.action == "check"
    cnn_idx = range( len(M) - 2 )
    for li in range(len(M)):
        if li in cnn_idx:
            nk, fm = M[li].get_weights()[0].shape[:2]
            state = load_state(li)
            prev_state = load_state(li - 1)
            yhat = act_f[li](prev_state.reshape((ds.X.shape[0], fm,
                                                 prev_state.shape[1] / fm, -1)))
        else:
            state = load_state(li)
            prev_state = load_state(li - 1).reshape( (ds.X.shape[0], -1) )
            yhat = act_f[li](prev_state)
        diff = np.max(np.abs(state.reshape((ds.X.shape[0], -1)) -
                             yhat.reshape((ds.X.shape[0], -1))), axis=0)
        print diff

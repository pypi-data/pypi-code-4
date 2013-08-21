#!/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""Train a convolutional neural net for classification"""

import sys
import argparse
import logging
import functools
from operator import attrgetter, concat
from collections import deque

import numpy as np
import theano
import theano.tensor as T

from dimer.archive import dset_path, DSPEC_MSG
from dimer.data import TrainAnchorDataset
from dimer.experiment import this_train_name
from dimer.nnet import nccn, monitor, verbose_compile, adjust_lr
from dimer.nnet.config_spec import ModelSpec, MtrainSpec

logging.basicConfig(level=logging.INFO)


if __name__ != "__main__":
    print >>sys.stderr, "this is a script. cannot import"
    sys.exit(1)

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    epilog="Olgert Denas (Taylor Lab)")
parser.add_argument("settings", type=str, help="Experiment file of settings.")
parser.add_argument("input", type=dset_path, help="Input data." + DSPEC_MSG)

parser.add_argument("--repfreq", type=int, default=1,
                    help="Frequency with which to print reports")
parser.add_argument("--seed", type=int, default=None,
                    help="Seed of random number generator")
parser.add_argument("--valid_size", type=float, default=0.2,
                    help="Fraction of the data for validation")
parser.add_argument("--valid_idx", type=int, default=4,
                    help=("Index from where to slice validation data from."
                          "In [0, |batches| - |valid_batches|]") )
parser.add_argument("--raw", action='store_true', default=False,
                    help=("Use the raw version of the data."
                          "Raw data are fitted in [0,1], but not normalized."))
opt = parser.parse_args()
log = logging.getLogger()

if opt.seed is None:
    opt.seed = np.random.randint(0, 100000)
log.warning("SEED is : %s", str(opt.seed))
rng = np.random.RandomState(opt.seed)

name_of_this_run = this_train_name(opt.settings, opt.seed)
log = logging.getLogger("%s" % name_of_this_run)


@verbose_compile
def compile_grad_f(layers, ds):
    "compile gradient function ..."

    params = reduce(concat, map(lambda l: l.get_params(), layers))
    index = T.iscalar("batch_index")
    in_bs = ds.batch_size
    dt_x, dt_y = ds.share("X", (-1, 1, ds.X.shape[1], ds.X.shape[2])), ds.shT

    return theano.function([index],
                           outputs=T.grad(layers.cost(tr.l1_rate, tr.l2_rate),
                                          wrt=params),
                           givens={layers.X: dt_x[index * in_bs:(index + 1) * in_bs],
                                   layers.Y: dt_y[index * in_bs:(index + 1) * in_bs]})


@verbose_compile
def compile_accurracy_f(layers, ds):
    "compile classification error function ..."

    index = T.iscalar("batch_index")
    in_bs = ds.batch_size
    dt_x, dt_y = ds.share("X", (-1, 1, ds.X.shape[1], ds.X.shape[2])), ds.shT
    return theano.function(inputs=[index],
                           outputs=T.sum( T.neq(layers[-1].y_hat, layers.Y) ),
                           givens={layers.X: dt_x[index * in_bs:(index + 1) * in_bs],
                                   layers.Y: dt_y[index * in_bs:(index + 1) * in_bs]})


@verbose_compile
def compile_cost_f(layers, ds):
    "compile the cost function ..."

    index = T.iscalar("batch_index")
    in_bs = ds.batch_size
    dt_x, dt_y = ds.share("X", (-1, 1, ds.X.shape[1], ds.X.shape[2])), ds.shT
    return theano.function(inputs=[index],
                           outputs=layers.cost(tr.l1_rate, tr.l2_rate),
                           givens={layers.X: dt_x[index * in_bs:(index + 1) * in_bs],
                                   layers.Y: dt_y[index * in_bs:(index + 1) * in_bs]})


@verbose_compile
def compile_ce_f(layers, ds):
    "compile the cross entropy function ..."

    index = T.iscalar("batch_index")
    in_bs = ds.batch_size
    dt_x, dt_y = ds.share("X", (-1, 1, ds.X.shape[1], ds.X.shape[2])), ds.shT
    return theano.function(inputs=[index], outputs=layers.cost(0, 0),
                           givens={layers.X: dt_x[index * in_bs:(index + 1) * in_bs],
                                   layers.Y: dt_y[index * in_bs:(index + 1) * in_bs]})


def main(ms, ds, tr):
    M = nccn.CnnModel((ms.nkerns, ms.rfield, ms.pool), ms.lreg_size,
                      (tr.batch_size, 1, ds.tracks, ds.width),
                      ds.labels, rng,
                      xdtype=ds.X.dtype, ydtype=str(ds.T.dtype))

    grad_f = compile_grad_f(M, ds)

    #monitor learning
    monitor_epoch = functools.partial(monitor.LearnMonitor._from_fs, ds=ds,
                                      cost_f=compile_cost_f(M, ds),
                                      ce_f=compile_ce_f(M, ds),
                                      mcl_f=compile_accurracy_f(M, ds))

    last_params = deque([], maxlen=tr.patience + 1)
    learning_info = []
    weight_info = []
    for epoch in range(tr.nepochs):
        learning_info.append( monitor_epoch(mtr=tr, epoch=epoch) )
        weight_info += map(lambda l: monitor.WeightMonitor._from_model(epoch, l, M),
                           range(len(M)) )

        if epoch % opt.repfreq == 0:
            log.info( learning_info[-1].report )

        ## step on the direction of gradient
        M.update_params(ds.train_batches, grad_f, tr.momentum_mult, tr.lr)

        ## reduce learning rate?
        if len(learning_info) > tr.tau:
            tr = tr._replace(lr=adjust_lr(map(attrgetter("validcost"), learning_info),
                                          tr.lr))

        ## continue at least for tr.minepochs epochs
        if epoch < tr.minepochs + tr.patience:
            last_params.append( M.get_weights() )
            continue

        ## done with minepochs + patience
        assert all( (len( learning_info ) >= tr.minepochs,
                     len(last_params) <= tr.patience + 1, epoch >= tr.minepochs) )

        ## has validMC gone up in all last paticence epochs? (min(patience) > paticence-1)
        if monitor.LearnMonitor.is_min_up("validcost", tr.patience, learning_info):
            log.info("validcost is up. Done training")
            assert last_params[0] == last_params[-tr.patience - 1], \
                ("len(last_params) is %d expected %d" % (len(last_params),
                                                         tr.patience + 1))
            ## restore the best parameters
            ## (from patience-1 i.e., the first element of last_params)
            M.weights = last_params[0]
            log.info("Restored best model from epoch %d", (epoch - tr.patience))
            return (M, learning_info[:-tr.patience], weight_info[:-tr.patience])
        else:
            if epoch % opt.repfreq == 0:
                log.info("non-increasing validcost. carry on")
            last_params.append( M.get_weights() )

    log.info("Hit maxepoch. Done training!")
    return (M, learning_info, weight_info)


ms, tr = map(lambda c: c._from_settings(opt.settings), (ModelSpec, MtrainSpec))
ds = TrainAnchorDataset._from_archive(opt.input, opt.raw, tr.batch_size,
                                      valid_s=opt.valid_size,
                                      valid_idx=opt.valid_idx, rng=rng )

model, learning_info, weight_info = main(ms, ds, tr)

monitor.LearnMonitor._archive_dump(opt.input, name_of_this_run, learning_info)
monitor.WeightMonitor._archive_dump(opt.input, name_of_this_run, weight_info)
model.save( opt.input + "/" + name_of_this_run )

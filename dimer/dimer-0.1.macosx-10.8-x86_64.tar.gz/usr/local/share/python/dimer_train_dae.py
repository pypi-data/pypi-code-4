#!/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python

"""Train a convolutional neural net for classification"""

import sys, argparse, pdb
import logging, functools
from operator import attrgetter, concat, itemgetter, attrgetter
from collections import deque

from dimer.archive import dset_path, DSPEC_MSG, this_train_name, get_target_dataset

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

if __name__ != "__main__":
    print >>sys.stderr, "this is a script. cannot import"
    sys.exit(1)

parser = argparse.ArgumentParser(description=__doc__,
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        epilog="Olgert Denas (Taylor Lab)")
parser.add_argument("settings", type=str, help="Experiment file of settings.")
parser.add_argument("input", type=dset_path, help="Input data."+DSPEC_MSG)
parser.add_argument("nhidden", nargs="+", type=int, help="Hidden dimensions. The last one is the output dimension.")
parser.add_argument("--clevel", type=float, default=0.0, help="Corruption level.")

parser.add_argument("--repfreq", type=int, default=1, help="Frequency with which to print reports")
parser.add_argument("--seed", type=int, default=None, help="Seed of random number generator")
opt = parser.parse_args()

import numpy as np
import theano
import theano.tensor as T
from theano.tensor.shared_randomstreams import RandomStreams
if opt.seed is None:
    seed = np.random.randint(0, 100000)
log.warning("SEED is : %s" % str(seed))
rng = np.random.RandomState(seed)
thrng = RandomStreams(rng.randint(2 ** 30))


from dimer.nnet import autoencoder, monitor, verbose_compile, adjust_lr
from dimer.nnet.config_spec import ModelSpec, MtrainSpec, DataSpec

ms, tr = map(lambda c: c._from_settings(opt.settings), (ModelSpec, MtrainSpec))
ds = DataSpec._from_archive(opt.input, tr.batch_size, rng)
name_of_this_run = this_train_name(opt.settings)
log = logging.getLogger("%s" % name_of_this_run)

## examples are set so that the validation samples are at the end
dt_x, dt_y = get_target_dataset(opt.input, 0, ds.train_s+ds.valid_s)
dt_x = theano.shared(dt_x.reshape((-1, ds.tracks*ds.width)),
        borrow=True)
dt_y = theano.shared(dt_y, borrow=True)

if np.any( dt_y.get_value() < 0 ):
    parser.error("targets contain negative values")



@verbose_compile
def compile_grad_f(model, in_bs, lidx, tr=tr):
    "compile gradient function ..."

    index = T.iscalar("batch_index")
    grad = T.grad(model[lidx].cost(tr.l1_rate, tr.l2_rate),
            wrt=model.get_params()[lidx])
    givens = {model[0].input : dt_x[index * in_bs : (index+1)*in_bs]}

    return theano.function([index], outputs=grad, givens=givens)

@verbose_compile
def compile_cost_f(model, in_bs, lidx):
    "compile the cost function ..."

    index = T.iscalar("batch_index")
    return theano.function(inputs=[index],
            outputs=model[lidx].cost(tr.l1_rate, tr.l2_rate),
                    givens={model[0].input : dt_x[index * in_bs:(index+1)*in_bs]})

def train_layer(model, lidx, tr=tr):
    grad_f = compile_grad_f(model, tr.batch_size, lidx)

    #monitor learning
    monitor_epoch = functools.partial(monitor.DaeLearnMonitor._from_fs,
            ds=ds, cost_f = compile_cost_f(model, tr.batch_size, lidx))

    last_params = deque([], maxlen=tr.patience+1)
    learning_info = []
    for epoch in range(tr.nepochs):
        learning_info.append( monitor_epoch(mtr=tr, epoch=epoch) )

        if epoch % opt.repfreq == 0:
            log.info( learning_info[-1].report )

        ## step on the direction of gradient
        model.update_params(ds.train_batches, grad_f, tr.momentum_mult, tr.lr, lidx)

        ## reduce learning rate?
        if len(learning_info) > tr.tau:
            tr = tr._replace(lr=adjust_lr(map(attrgetter("traincost"),
                learning_info), tr.lr))

        ## continue at least for tr.minepochs epochs
        if epoch < tr.minepochs + tr.patience:
            last_params.append( model.get_weights() )
            continue

        ## done with minepochs + patience
        assert all( (len( learning_info ) >= tr.minepochs,
            len(last_params) <= tr.patience + 1, epoch >= tr.minepochs) )

        ## has validMC gone up in all last paticence epochs? (min(patience) > paticence-1)
        if monitor.Monitor.is_min_up("validcost", tr.patience, learning_info):
            log.info("validcost is up. Done training")
            assert last_params[0] == last_params[-tr.patience-1], ("len(last_params) is %d"
                    "expected %d" % (len(last_params), tr.patience+1))
            ## restore the best parameters (from patience-1 i.e., the first element of last_params)
            model.weights = last_params[0]
            log.info("Restored best model from epoch %d"  % (epoch - tr.patience))
            return learning_info[:-tr.patience]
        else:
            if epoch % opt.repfreq == 0:
                log.info("non-increasing validcost. carry on")
            last_params.append( model.get_weights() )
    log.info("Hit maxepoch. Done training!")
    return learning_info


def main():
    M = autoencoder.AEStack( ds.width*ds.tracks, opt.nhidden, rng, thrng,
                dt_x.get_value().dtype, opt.clevel )


    for i in range(len(M)):
        log.info("training layer %d %s ...", i, str(M[i]))
        linfo = train_layer(M, i)

main()


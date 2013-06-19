import scipy as SP
# import lmm and whatever is needed
import logging as LG
import scipy as SP
import cPickle
import os
import sys

#LOAD LMM
try:
    #import panama.core.lmm.lmm as LMM
    import lmm.lmm as LMM
except ImportError:
    LG.error("Fast C++ LMM not available, falling back to python version")
    import lmm.lmm_fast as LMM

delta_opt_params_default={'numintervalsAlt':0,
                    'ldeltaminAlt':-1.0, 'ldeltamaxAlt':1.0,
                    'numintervals0':100,
                    'ldeltamin0':-5.0, 'ldeltamax0':5.0}


def hdf5_load_data(in_file,index_s,index_p):
    """
    loads data from hdf5 file
    """
    import h5py
    # read arguments from hdf5 instead of assuming they are passed form local memory
    f = h5py.File(in_file,'r')
    S = SP.array(f['S'][:,index_s])
    P = SP.array(f['P'][:,index_p])
    K = SP.array(f['K'])
    covs = SP.array(f['covs'])
    I = None
    if 'I' in f.keys():
        I = SP.array(f['I'])
    return S, P, K,covs,I


def filter_dict(D,keys):
    """
    filter_dict
    """
    for key in D.keys():
        if key not in keys:
            del(D[key])
    return D


def wrapper(S, P, K, covs = None, I = None, index_p=None, index_s=None, model = 'LMM',
	    return_fields= ['pv'], path_append=[], out_file= None, in_file=None,
	    Ftest = True, delta_opt_params=None):
    """wrapper"""
    
    import sys
    #raise Exception(path_append)
    sys.path.extend(path_append)
    #print sys.path
    # from testing_core import * #FIXME uncomment for old-style parallel

    if delta_opt_params is None:
        delta_opt_params = delta_opt_params_default

    #load hdf5 data if specified
    if in_file is not None:
        S, P, K,covs,I = hdf5_load_data(in_file,index_s,index_p)
        
    # load existing dump file if available 
    if (out_file is not None) and os.path.exists(out_file):
	f = open(out_file,'rb')
        rv = cPickle.load(f)
	f.close()
        filter_dict(rv,return_fields)
        return rv

    #return value is a hash of results that depends on actual method
    rv = {}
    if model=='LMM':
        if I is not None:
            lod,pval =  LMM.train_interactions(S, P, K, covs, I, use_ftest = Ftest, **delta_opt_params)
        else:
	    lod, pval =  LMM.train_associations(S, P, K, covs, **delta_opt_params)

        lod = lod.T
        pval = pval.T
    else:
        # ML
        if I is not None:
            print "not implemented!"
            pass
        else:
	    lod = linreg.run_associations(P, S, None)
	    pval = (1. - st.chi2.cdf(2*lod, 1))
    rv['index_p'] = index_p
    rv['index_s'] = index_s 
    rv['lod'] = lod
    rv['pv'] = pval
    # dump to file if specified
    if out_file is not None:
	f = open(out_file,'wb')
        cPickle.dump(rv,f,-1)
	f.close()
        return out_file
    else:
        #return 
        filter_dict(rv,return_fields)
        return rv

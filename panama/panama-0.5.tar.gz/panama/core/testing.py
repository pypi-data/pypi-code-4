"""
Association and interaction testing module for PANAMA
(1) association testing
(2) interaction testing
(3) parallelization using ipython
"""

import sys, os, string, cPickle, copy, pdb
import logging as LG
import scipy as SP
import numpy as N
import scipy.stats as st
import copy
import testing_core

try:
    from IPython.kernel import client
    ipy_version = 0.10
except ImportError:
    from IPython.parallel import Client as client
    ipy_version = 0.12

tc_clients = None

def interface(S, P, K, covs = None, I = None, model = 'LMM', return_fields= ['pv'], parallel = False,
	      add_mean = True, jobs = 1, file_directory=None, delta_opt_params=None, Ftest = False):

    """
    interface function for association testing
    S: SNPS [indiv X snps]
    Y: expr [indic X genes]
    covs: covariates 

    return_filed: fields to caculate and return
    file_directory: if provided data handling and result storing will be handled via file IO
    delta_opt_params: parameters for delta optimization 
    """

    #1. check dimensions
    [Nn, Np] = P.shape
    Ns       = S.shape[1]

    #check input arguments
    assert (S.shape[0]==Nn), 'dimension error'
    if K is not None:
        assert (K.shape[0]==Nn), 'dimension error'
        assert (K.shape[1]==Nn), 'dimension error'
    if I is not None:
        assert (I.shape[0]==Nn), 'dimension error'
    #covariates: 
    if covs is None:
	covs = SP.zeros([Nn,0])
        if add_mean:
            #add mean column ( we should generally do this )
            covs = SP.concatenate((covs,SP.ones([Nn,1])),axis=1)

    #figure out base path
    cwd=os.getcwd()
    base_path      = os.path.dirname(__file__)
    glob_base_path = os.path.join(cwd,base_path)
    paths = [glob_base_path]

    if file_directory is not None:
        if not os.path.exists(file_directory):
            print "file mode for testing specified but directory %s not existing; disableing" % file_directory

    #check whether to use file mode
    file_mode = ((file_directory is not None) and os.path.exists(file_directory))
    #setup file handling if switched on
    in_file = None
    in_file_path = None
    out_file = None
    out_file_base = None
    if file_mode:
        import h5py
        in_file = os.path.join(file_directory,'data.hdf5')
	in_file_path = os.path.abspath(in_file)
        out_file_base = os.path.join(file_directory,'result_')
        #store matrix objects
        _data = {'S':S,'P':P,'K':K,'I':I,'covs': covs}
        f = h5py.File(in_file,'w')
        for key in _data:
            if _data[key] is None:
                continue
            f.create_dataset(name=key,data=_data[key],chunks=True)
        f.close()
        del(f)

    if not parallel:
        RV = testing_core.wrapper(S, P, K, covs = covs, I = I, model = model,
				  path_append = paths,index_s = SP.arange(S.shape[1]),
				  index_p = SP.arange(P.shape[1]),
				  in_file = in_file_path,
				  delta_opt_params=delta_opt_params, Ftest = Ftest)        
    else:
	# setup engines and perform checks
	tc, eng_ids = start_engines(jobs)

	# split the data according to the number of jobs
        #note jobs is the max. number of jobs...
	Y_split = split_jobs(P, jobs)

	ipython_jobs = []
	for n in xrange(len(Y_split)):
	    i0 = Y_split[n][0]
	    i1 = Y_split[n][1]
	    P_n = Y_split[n][2]

            #arguments of job
            #convert all paths to absolute paths
            xargs=SP.array([S, P_n, K, covs, I, range(i0, i1), range(S.shape[1]),
			    model, return_fields, paths, out_file, in_file_path,
			    Ftest, delta_opt_params],dtype='object')
            #if in file_mode, overwrite:
            if file_mode:
                out_file = '%s%03d.pickle' % (out_file_base,n)
                if os.path.exists(out_file):
                    os.remove(out_file)
                xargs[0:4] = None
                xargs[-3]  = os.path.abspath(out_file)

	    if ipy_version == 0.10:
		job = client.MapTask(testing_core.wrapper, xargs.tolist())
		ipython_jobs.append(tc.run(job))
	    else:
		dview = eng_ids[:]
		lbview = tc.load_balanced_view()
		job = lbview.apply(testing_core.wrapper, *xargs.tolist())
		ipython_jobs.append(job)
	    
        #wait for job completion:
	if ipy_version == 0.10:
	    tc.barrier(ipython_jobs)
	else:
	    tc.wait(ipython_jobs)

	RV = None
	for n in xrange(len(Y_split)):
	    i0 = Y_split[n][0]
	    i1 = Y_split[n][1]

            #fecht results from job
	    if ipy_version == 0.10:
		_rv = tc.get_task_result(ipython_jobs[n])
	    else:
		_rv = ipython_jobs[n].get()
	    
            if isinstance(_rv,str):
		f = open(_rv,'rb')
                _rv = cPickle.load(f)
		f.close()
                _rv = testing_core.filter_dict(_rv,return_fields)

            #do we need to create result structures?
            if RV is None:
                RV = {}
                #get shape of all fields we need
                #append dimensions form result structure
                for key in _rv.keys():
                    val = _rv[key]
                    dim0 = [Ns,Np]
                    dim0.extend(list(val.shape[2::]))
                    RV[key] = SP.empty(dim0)
            #slot in result fileds
            for key in _rv.keys():
                RV[key][:,i0:i1] = _rv[key]
    return [RV[key] for key in return_fields]


#### internal helper functions ####


 
        

def split_jobs(Y, Njobs):
    #slit phenotype matrix into jobs
    #think about splitting snps also
    splits = []


    [N, Np] = Y.shape
    #maximal splitting range is one job per phenotype
    Njobs = min(Njobs,Np)

    #figure out phenotypes per job (down rounded)
    npj   = int(SP.floor(SP.double(Np)/Njobs))
    
    i0 = 0
    i1 = npj
    for n in xrange(Njobs):
        if n==(Njobs-1):
            #make sure last jobs spans all the rest.
            i1 = Np
        Y_ = Y[:,i0:i1]
	splits.append([i0, i1, Y_])
        #nex split
        i0 = i1
        i1 = i1 + npj
        
    return splits

def start_engines(jobs):
    """
    Starts the engines and performs some checks

    jobs: int
    """

    global tc_clients
    
    if ipy_version == 0.10:
	tc = client.TaskClient()
	mec = client.MultiEngineClient()
	eng_ids = mec.get_ids()
    else:
	if tc_clients == None:
	    tc = client()
	    eng_ids = tc.ids
	    tc_clients = tc
	else:
	    tc = tc_clients
	    eng_ids = tc.ids
	
    #reset engines
    #mec.reset()
    assert eng_ids > 0, "No engine started"	
    #assert eng_ids > jobs, "Not enough engines for the number of jobs required"

    return tc, eng_ids

                


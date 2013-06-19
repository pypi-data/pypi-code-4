import lmm
#import lmm
import sys
import scipy.linalg as LA
import cPickle
#import standard fast python lmm
sys.path.append('./../core')
import lmm_fast
import scipy as SP
import pdb
#import pylab as PL

#TODO
#load data with SNPS x and phenotype matrix Y
X, Y, K = cPickle.load(open("S_Y_K_testing.pickle", "r"))
#run standard lmm
#X = SP.random.randn(X.shape[0],10000)

n,s=X.shape;
n_pheno=Y.shape[1];
S,U=LA.eigh(K);
UY=SP.dot(U.T,Y);
UX=SP.dot(U.T,X);


ldelta = +8

import time

#need to create copies to ensure it is all properly lined up in memory
#TODO: I am sure this issues is common to cython stuff and other people have similar problems
_UX = SP.array(UX[:,0:2])
_UY = SP.array(UY[:,0])

if 1:
    print "testing delta opt"
    delta0 = lmm_fast.optdelta(_UY,_UX,S)
    delta1 = lmm.optdelta(_UY,_UX,S)
    print "%.2f versus %.2f" % (delta0,delta1)

if 1:
    print "testing eval on all SNPs"
    for i in xrange(UX.shape[1]):
        _UX = UX[:,i:i+1]
        _UY = SP.array(UY[:,0])
        lml0=lmm_fast.nLLeval(ldelta,_UY,_UX,S)
        lml1=lmm.nLLeval(ldelta,_UY,SP.array(_UX),S)
        lml2=lmm.nLLeval(ldelta,_UY,_UX,S)
        assert SP.absolute(lml1-lml2)<1E-10, 'outch'
        print "lml: %.2f delta lml (rel) : %.2f " % (lml1,(lml1-lml0)/SP.absolute(lml1))
       

if 0:
    covariates = SP.ones([X.shape[0],1])

    t0=time.time()
    LOD0 = lmm.train_associations(X,Y,K,covariates)
    print "t1"
    t1=time.time()
    LOD1 = lmm.train_interactions(X,Y,K,X[:,0:1],covariates,refit_delta0_snp=False)
    print "t2"
    t2=time.time()
    LOD2 = lmm.train_interactions(X,Y,K,X[:,0:10],covariates,refit_delta0_snp=False)
    print "t3"
    t3=time.time()
    LOD2 = lmm.train_interactions(X,Y,K,X[:,0:100],covariates,refit_delta0_snp=False)
    t4=time.time()
    

if 1:
    print "testing train method on all data"
    covariates = SP.ones([X.shape[0],1])
    LOD0 = lmm.train_associations(X,Y,K,covariates)

    kw_args = {'numintervalsAlt':0,'ldeltaminAlt':-1.0,'ldeltamaxAlt':1.0,'numintervals0':100,'ldeltamin0':-10.0,'ldeltamax0':10.0}
    t0 = time.time()
    LOD1 = lmm.train_associations(X,Y,K,covariates,**kw_args)[0]
    t1 = time.time()
    #compare the whole thing
    [LL0, LL, pval, ldelta0, sigg20, beta0, ldelta, sigg2, beta] = lmm_fast.train(X,Y,K,covariates,addBiasTerm=False,**kw_args)
    LOD2 = LL-LL0
    t2 = time.time()
    print SP.absolute(LOD1-LOD2).max()


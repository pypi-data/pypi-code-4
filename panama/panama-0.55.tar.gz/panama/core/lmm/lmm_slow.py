import scipy as SP
import scipy.linalg as LA
import scipy.optimize as OPT
import scipy.stats as st
from pygp.linalg import *
import scipy.lib.lapack.flapack
import pdb

def nLLeval(ldelta,X,Y,K):
    """evaluate the negative LL of a LMM with kernel USU.T"""
    delta=SP.exp(ldelta)
    H = K + delta*SP.eye(X.shape[0])
    #the slow way: compute all terms needed
    L = jitChol(H)[0].T # lower triangular
    Linv = scipy.lib.lapack.flapack.dpotri(L)[0]
    Kinv = Linv.copy()
    SP.fill_diagonal(Linv, 0)
    Kinv += Linv.T
    n = X.shape[0]

    #1. get max likelihood weight beta
    pinv = SP.dot(SP.linalg.inv(SP.dot(SP.dot(X.T,Kinv),X)),X.T)
    y_   = SP.dot(Kinv,Y)
    beta = SP.dot(pinv,y_)
    #2. get max likelihood sigma
    yres = (Y-SP.dot(X,beta))
    R = SP.dot(SP.dot(yres.T,Kinv),yres)
    sigma2 = R/n

    nLL = 0.5*(-n*SP.log(2*SP.pi*sigma2) - 2*SP.log(L.diagonal()).sum() - 1./sigma2*R)
    return (-nLL);



def optdelta(X,Y,K,ldeltanull=None,numintervals=100,ldeltamin=-5.0,ldeltamax=5.0):
    """find the optimal delta"""
    if ldeltanull==None:
        nllgrid=SP.ones(numintervals+1)*SP.inf;
        #nllgridf=SP.ones(numintervals+1)*SP.inf;
        ldeltagrid=SP.arange(numintervals+1)/(numintervals*1.0)*(ldeltamax-ldeltamin)+ldeltamin;
        nllmin=SP.inf;
        ldeltamin=None;
        for i in SP.arange(numintervals+1):
            #nllgridf[i]=nLLevalf(ldeltagrid[i],UY,UX,S);
            nllgrid[i]=nLLeval(ldeltagrid[i],X,Y,K);
            if nllgrid[i]<nllmin:
                nllmin=nllgrid[i];
                ldeltamin=ldeltagrid[i];
        for i in SP.arange(numintervals-1)+1:
            ee=1E-8
            if ( ((nllgrid[i-1]-nllgrid[i])>ee) and (nllgrid[i+1]-nllgrid[i])>ee):
                #search within brent if needed
                ldeltaopt,nllopt,iter,funcalls = OPT.brent(nLLeval,(X,Y,K),(ldeltagrid[i-1],ldeltagrid[i],ldeltagrid[i+1]),full_output=True);
                if nllopt<nllmin:
                    nllmin=nllopt;
                    ldeltamin=ldeltaopt;
    else:
        ldeltamin=ldeltanull;
        #nllminf=nLLevalf(ldeltamin,UY,UX,S);
        nllmin=nLLeval(ldeltamin,X,Y,K);
        #assert SP.absolute(nllmin-nllminf)<1E-5, 'outch'
    return nllmin,ldeltamin;

def train(X,Y,K,covariates=None):
    """ compute all pvalues """
    n,s=X.shape;
    n_pheno=Y.shape[1];
    Xcovariate = SP.ones([X.shape[0],1])
    LL=SP.ones((n_pheno,s))*(-SP.inf);
    LL0=SP.ones((n_pheno))*(-SP.inf);
    pval=SP.ones((n_pheno,s))*(-SP.inf);
    for phen in SP.arange(n_pheno):
        nllnull,ldeltanull=optdelta(Xcovariate,Y[:,phen],K,ldeltanull=None,numintervals=100,ldeltamin=-5.0,ldeltamax=5.0);
        LL0[phen]=-nllnull;
        for snp in SP.arange(s):
            nll,ldelta=optdelta(SP.concatenate((X[:,snp:snp+1],Xcovariate),axis=1),Y[:,phen],K,ldeltanull=ldeltanull,numintervals=5,ldeltamin=ldeltanull-1.0,ldeltamax=ldeltanull+1.0);
            LL[phen,snp]=-nll;
            #calculate pvalues
            pval[phen,snp]=(st.chi2.sf(2.*(LL[phen,snp]-LL0[phen]), 1))
    return pval, LL0, LL

def eigenstratImputation(X, maxval=2.0):
    """
    impute SNPs as in
    'Principle components analysis corrects for stratification in genome-wide association studies'
    Price et al 2006 (Nature Genetics) page 908, Section 'Methhods', 'Inference of axes of variation'

    Input:
      X:        [n_indiv * n_SNP] matrix of SNPs, missing values are SP.nan
      maxval:   maximum value in X (default is 2 assuming 012 encoding)

    Output:
      X_ret:        [n_ind * n_SNP] matrix of imputed and standardized SNPs
    """
    n_i,n_s=X.shape
    X_ret=X.copy()
    for snp in SP.arange(n_s):
        i_nonan=X[:,snp]==X[:,snp]
        n_obs=SP.sum(i_nonan)
        snp_sum=SP.sum(X[i_nonan,snp])
        one_over_sqrt_pi=(1.+snp_sum)/(2.0+maxval*n_obs)
        one_over_sqrt_pi=1./SP.sqrt(one_over_sqrt_pi*(1.-one_over_sqrt_pi))
        snp_mean=(snp_sum*1.0)/(n_obs*1.0)
        X_ret[i_nonan,snp]-=snp_mean
        X_ret[i_nonan,snp]*=one_over_sqrt_pi
    X_ret[X!=X]=0.0
    return X_ret

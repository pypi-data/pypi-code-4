'''
Created on Nov 5, 2010

@author: jonathanfriedman

Module for estimating the correlations in the basis when only compositional data is available.
'''

import numpy as np
from numpy import array, zeros, tile, ones, log, corrcoef, var, exp, cov, r_, diag, matrix, diag, sqrt, where
from numpy.linalg import det, pinv
from pysurvey.core.core_methods import to_fractions
from pysurvey.core.compositional_methods import variation_mat    
from pysurvey.analysis.analysis_methods import correlation

def append_indices(excluded,exclude):
    '''
    Append the indx of current excluded value to tuple of previously excluded values.
    '''
    if excluded is None: inds = exclude
    else:                inds = (r_[excluded[0],exclude[0]], r_[excluded[1],exclude[1]])
    return inds
    
def exclude_pairs(C, M, th=0.1, excluded=None):
    '''
    Exclude pairs with high correlations.
    '''
    break_flag = False
    C_temp = abs(C - diag(diag(C)) )
    if excluded is not None: C_temp[excluded] = 0 # set previously excluded correlations to 0.
    temp    = where(C_temp == C_temp.max())
    i       = temp[0][0,1]
    j       = temp[1][0,1]
    exclude = (np.matrix([i,j]), np.matrix([j,i]))
    if C_temp.max() > th:
        M[exclude] -= 1 
        for i in exclude[0]:
            M[i,i] -= 1
        excluded_new = append_indices(excluded,exclude)
    else:
        excluded_new = excluded
        break_flag   = True
    return M, excluded_new, break_flag

def basis_var(f, V_mat, **kwargs):
    '''
    Estimate the variances of the basis of the closed data x.
    Assumes that the correlations are sparse (mean correlation is small).
    '''
    from copy import deepcopy
    k        = len(V_mat)
    excluded = kwargs.get( 'excluded', None )
    V_mat_copy = deepcopy(V_mat) 
    if excluded is not None: V_mat_copy[excluded] = 0
    V_vec    = V_mat_copy.sum(axis = 1)
    Cov_mat  = kwargs.get( 'Cov_mat', matrix(zeros((k,k))) )
    Cov_vec  = (Cov_mat - diag(diag(Cov_mat)) ).sum(axis = 1)
    ## compute basis variances
    M = kwargs.get( 'M', matrix( ones((k,k)) + diag([k-2]*k) ) )
    try:    M_inv = M.I
    except: M_inv = pinv(M)
    V_base = M_inv * (V_vec + 2* Cov_vec)
    ## if any variances are <0 set them to V_min
    V_min  = kwargs.get('V_min', 1e-4)
    V_base[V_base < 0] = V_min 
    return V_base, M

def C_from_V(Var_mat, V_base):
    '''
    Given the estimated basis variances and observed fractions variation matrix, compute the basis correlation & covaraince matrices
    '''
    k        = len(V_base)
    Cov_base = matrix( zeros((k,k)) )
    C_base   = matrix( zeros((k,k)) )
    for i in range(k-1):
        Cov_base[i,i] = V_base[i]
        C_base[i,i]   = 1.0
        for j in range(i+1,k):
            Cov_base_temp = 0.5*(V_base[i] + V_base[j] - Var_mat[i,j])
            cor_base_temp = Cov_base_temp/ sqrt(V_base[i]) / sqrt(V_base[j])
            if np.abs(cor_base_temp) > 1: #check if got valid correlation value (-1 < cor < 1)
                cor_base_temp = np.sign(cor_base_temp)
                Cov_base_temp = cor_base_temp* sqrt(V_base[i]) * sqrt(V_base[j])
            Cov_base[i,j] = Cov_base_temp
            Cov_base[j,i] = Cov_base[i,j]
            C_base[i,j]   = cor_base_temp
            C_base[j,i]   = C_base[i,j]
            if np.isnan(C_base[i,j]):
                print V_base[i], V_base[j], Var_mat[i,j] 
    Cov_base[k-1,k-1] = V_base[k-1]
    C_base[k-1,k-1]   = 1.0
    return C_base, Cov_base

def basis_corr(f, method='sparcc', **kwargs):
    '''
    Estimate the correlations of the basis of the closed data x.
    Assumes that the correlations are sparse (mean correlation is small).
    '''
    th   = kwargs.get('th', 0.1)
    n, k = f.shape
    ## observed log-ratio variances
    shrink  = kwargs.get('shrink', False)
    Var_mat = variation_mat(f, shrink=shrink)
    ## compute basis variances & correlations
    if method == 'clr':
        if k<4: 
            raise ValueError, 'Can not detect correlations between compositions of <4 components (%d given)' %k 
        z        = f.clr(**kwargs)
        Cov_base = cov(z, rowvar = 0)
        C_base   = corrcoef(z, rowvar = 0)
        V_base   = diag(Cov_base)
    elif method == 'sparcc':
        if k<4: 
            raise ValueError, 'Can not detect correlations between compositions of <4 components (%d given)' %k   
        V_base, M        = basis_var(f, Var_mat)
        C_base, Cov_base = C_from_V(Var_mat, V_base)
        iter     = kwargs.get('xiter', 10)
        excluded = None
        for i in range(iter):
            M, excluded, break_flag = exclude_pairs(C_base, M, th = th, excluded = excluded)
            if break_flag: break
            V_base, M        = basis_var(f, Var_mat, M = M, excluded = excluded)
            C_base, Cov_base = C_from_V(Var_mat, V_base)
        if np.max(np.abs(C_base)) > 1.0:
            V_base, C_base, Cov_base = basis_corr(f, method='clr', **kwargs)    
    elif method == 'csi':  
        p, V_base = f.CSI_test()
        V_base, M        = matrix(V_base).transpose()
        C_base, Cov_base = C_from_V(Var_mat, V_base)
    return V_base, C_base, Cov_base 

def main(counts, method='SparCC', **kwargs):
    '''
    Compute correlations between all components of counts matrix.
    
    Parameters
    ----------
    counts : array_like
        2D array of counts. Columns are counts, rows are samples. 
    method : str, optional (default 'SparCC')
        The algorithm to use for computing correlation.
        Supported values: SparCC, clr, pearson, spearman, kendall

    Returns
    -------
    cor_med: array
        Estimated correlation values.
    cov_med: array
        Estimated covariance matrix if method in {SparCC, clr},
        None otherwise.
              
    =======   ============ =======   ================================================
    kwarg     Accepts      Default   Desctiption
    =======   ============ =======   ================================================
    iter      int          20        number of estimation iteration to average over.
    oprint    bool         True      print iteration progress?
    th        0<th<1       0.1       exclusion threshold for SparCC.
    xiter     int          10        number of exclusion iterations for sparcc.
    norm      str          dirichlet method used to normalize the counts to fractions.
    log       bool         True      log-transform fraction? used if method ~= SparCC/CLR
    =======   ============ ========= ================================================
    '''
    method = method.lower()
    cor_list = []  # list of cor matrices from different random fractions
    var_list = []  # list of cov matrices from different random fractions
    oprint   = kwargs.pop('oprint',True)
    iter     = kwargs.pop('iter',20)  # number of iterations 
    th       = kwargs.pop('th',0.1)   # exclusion threshold for iterative sparse algo
    norm     = kwargs.pop('norm','dirichlet')
    log      = kwargs.pop('log','True')
    if method in ['sparcc', 'clr']: 
        for i in range(iter):
            if oprint: print '\tRunning iteration ' + str(i)
            fracs = to_fractions(counts, method=norm)
            v_sparse, cor_sparse, cov_sparse = basis_corr(fracs, method=method, **kwargs)
            var_list.append(np.diag(cov_sparse))
            cor_list.append(cor_sparse)
        cor_array = np.array(cor_list)
        var_med = np.median(var_list,axis = 0) #median covariance
        cor_med = np.median(cor_array,axis = 0) #median covariance
        x,y     = np.meshgrid(var_med,var_med)
        cov_med = cor_med * x**0.5 * y**0.5
    elif method in ['pearson', 'kendall', 'spearman']:
        for i in range(iter):
            if oprint: print '\tRunning iteration ' + str(i)
            fracs = to_fractions(counts, method=norm)
            if log:
                x = np.log(fracs)
            else:
                x = fracs
            cor_mat, pval = correlation(x, method, axis=0)
            cor_list.append(cor_mat)
        cor_array   = np.array(cor_list)
        cor_med = np.median(cor_array, axis=0) #median correlation
        cov_med = None 
    return cor_med, cov_med 

if __name__ == '__main__':
    x = np.arange(1,10)
#    y = np.ones(len(x))
#    X = np.c_[x,y]
#    X = np.random.rand(200,3)
#    cor,cov =  main(X, 'clr', oprint=0)  
#    print cor      



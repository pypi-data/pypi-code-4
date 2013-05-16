'''
========================
Matrix Utility Functions
========================
'''

__all__ = ['matrix_rank']

__author__ = '''Nicholas Mancuso (nick.mancuso@gmail.com)'''
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

from numpy.linalg import svd
from numpy import sum, where


# Found at...
# http://mail.scipy.org/pipermail/numpy-discussion/2008-February/031218.html
def matrix_rank(matrix, tol=1e-8):
    '''
        Compute the rank of a matrix
        using the singular value decomposition
        and counting the non-zero rows
    '''
    s = svd(matrix, compute_uv=0)
    return sum(where(s > tol, 1, 0))

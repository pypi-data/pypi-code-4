#! /usr/bin/python
# -*- coding: utf-8 -*-


#If you have any questions, please contact any of the following:
#Evan(evan176@hotmail.com)

import sys, numpy

###############################################################################

#Do gaussian kernel
#Input:
#gamma = width parameter; kernel value: exp(-gamma(Ai-Aj)^2)
#A = full data set
#tildeA = can be full or reduced set
#Output:
#K = kernel data using Gaussian kernel 

#-------------------------------------------------------------------------------

#建置高斯kernel matrix
#輸入：
#gamma = 高斯的調整值; kernel value: exp(-gamma(Ai-Aj)^2)
#A = a [m x n] real number matrix
#tildeA = can be full or reduced set
#輸出：
#K = 使用高斯kernel建置出的kernel matrix

###############################################################################
def gaussianKernel(gamma, A, tildeA=numpy.array([])):


    #Set limit on data matrix : A and tildeA
        #設定矩陣 A, tildeA 的限制
    if (not isinstance(A, numpy.ndarray)) or (not isinstance(tildeA, numpy.ndarray)):
        print '\n===Error in gaussianKernel : A or tildeA must be 2d-array==='
        sys.exit(1)
    if tildeA.size > 0:
        if A.shape[1] != tildeA.shape[1]:
            print '\n===Error in gaussianKernel : A index must equal to tildeA==='
            sys.exit(1)

        AA = numpy.kron(numpy.ones((1, tildeA.shape[0])), numpy.sum(A ** 2, axis=1).reshape(A.shape[0], 1))
        tildeAA = numpy.kron(numpy.ones((1, A.shape[0])), numpy.sum(tildeA ** 2, axis=1).reshape(tildeA.shape[0], 1))
        K = numpy.exp(( -AA - tildeAA.transpose() + 2 * numpy.dot(A, tildeA.transpose())) * gamma)

        return K
    else:
        AA = numpy.kron(numpy.ones((1, A.shape[0])), numpy.sum(A ** 2, axis=1).reshape(A.shape[0], 1))
        K = numpy.exp(( -AA - AA.transpose() + 2 * numpy.dot(A, A.transpose())) * gamma)

        return K


###############################################################################

#Build kernel data matrix, no matter matrix is full or reduced
#Input:
#params = determine which matrix want to create: linear or nonlinaer
#A = A is a [m x n] real number matrix
#tildeA = a [p x n] real number matrix
#gamma = kernel arguments(it dependents on your kernel type)
#Output:
#K = flag + Kernel
#    flag -> indicate which type is
#    Kernel -> kernel matrix 

#-------------------------------------------------------------------------------

#建置kernel matrix，不論輸入的是full set 或者 reduced set
#輸入：
#params = 決定要建置linear or nonlinear的matrix
#A = a [m x n] real number matrix
#tildeA = a [p x n] real number matrix
#gamma = RBF的調整值
#輸出：
#K = flag + Kernel
#    flag -> 用來指名matrix的型態: 'primal' or 'dual'
#    Kernel -> kernel matrix 


###############################################################################
def buildKernel(params, gamma, A, tildeA=numpy.array([])):


    #Set limit on data matrix : A
        #設定矩陣 A 的限制
    if (not isinstance(A, numpy.ndarray)) or (not isinstance(tildeA, numpy.ndarray)):
        print '\n===Error in build_kernel : A or tildeA must be 2d-array==='
        sys.exit(1)

    #Build nonlinear matrix
    #建置非線性矩陣
    if params == 1:
        if tildeA.size > 0:
            K = {'flag': 'dual', 'Kernel': gaussianKernel(gamma, A, tildeA)}
        else:
            K = {'flag': 'dual', 'Kernel': gaussianKernel(gamma, A)}
    #Build linear matrix
    #建置線性矩陣
    elif params == 0:   
        if A.shape[1] > A.shape[0] and tildeA.size > 0:
            K = {'flag': 'dual', 'Kernel': numpy.dot(A, tildeA.transpose())}
        else:
            K = {'flag': 'primal', 'Kernel': A}
    else:
        K = {'flag': 'dual', 'Kernel': A}

    return K




########################################Test Area########################################
"""
A=array([[2,3,4],[4,5,6],[-1,0,1]])
B=array([[3,1,-9],[-18,100,101],[3,4,5]])
K=build_kernel(1,0.5,A)
print K
"""

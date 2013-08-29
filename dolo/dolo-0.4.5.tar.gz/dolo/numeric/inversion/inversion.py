from __future__ import division

import numpy

from numbapro import autojit
from numbapro.vectorize import GUVectorize
from numbapro import float32, float64, cuda, guvectorize, void

dtype = numpy.float64
nb_dtype = float64

target = 'gpu'


def mult(A, B, C):
    m, n = A.shape
    for i in range(n):
        for j in range(m):
            C[i] += A[i, j] * B[j]
    return C


@guvectorize([ void(nb_dtype[:,:], nb_dtype[:]) ], '(m,n)->(m)', target=target)
def solve(m,sol):

    h,w = m.shape

    for y in range(0,h):
        maxrow = y
        for y2 in range(y+1, h):    # Find max pivot
            if abs(m[y2,y]) > abs(m[maxrow,y]):
                maxrow = y2
        for y2 in range(0,w):
            t = m[y,y2]
            m[y,y2] = m[maxrow,y2]
            m[maxrow,y2] = t
#        t = m[y,:].copy()
#        m[y,:] = m[maxrow,:].copy()
#        m[maxrow,:] = t
    #    if abs(m[y][y]) <= eps:     # Singular?
    #      return False
        for y2 in range(y+1, h):    # Eliminate column y
            c = m[y2,y] / m[y,y]
            for x in range(y, w):
                m[y2,x] -= m[y,x] * c
    for y in range(h-1, 0-1, -1): # Backsubstitute
        c  = m[y,y]
        for y2 in range(0,y):
            for x in range(w-1, y-1, -1):
                m[y2,x] -=  m[y,x] * m[y2,y] / c
        m[y,y] /= c
        for x in range(h, w):       # Normalize row y
          m[y,x] /= c

#    sol[:] = m[:,w-1]
    for y in range(h):
        sol[y] = m[y,w-1]

#    return sol
#    ores[:] = res[:]
#    for i in range(h):
#        temp[i] = (m[i,w])

#    temp[0] = 1
#    m[0,w] = 2
#    print(m.shape)
#    print(m[4,5])
#    print(h)
    
#    for y in range(h):

#    return res

def solve_numpy(A,Y):
    A = numpy.rollaxis(A,2,0)
    Y = numpy.rollaxis(Y,1,0)
    N,m,n = A.shape
    assert(m == n)
    X = numpy.zeros( (N, m) )
    for i in range(N):
        X[i,:] = numpy.linalg.solve(A[i,:,:], Y[i,:])
    X = numpy.rollaxis(X,1,0)
    return X

#print('going to compile')
#gufunc = GUVectorize(solve, '(m,n)->(m)', target='gpu') #, backend='ast')
#gufunc.add(argtypes=[float32[:,:], float32[:]])
#gufunc.add(argtypes=[float64[:,:], float64[:]])
#gufunc = gufunc.build_ufunc()

#solve.max_bocksize = 32


gufunc2 = GUVectorize(mult, '(m,n),(n)->(m)', backend='ast')
gufunc2.add(argtypes=[float32[:,:], float32[:,:], float32[:,:]])
gufunc2.add(argtypes=[float64[:,:], float64[:,:], float64[:,:]])
gufunc2 = gufunc2.build_ufunc()

print('compiled')

#ufunc = gufunc.build_ufunc()
#
#    res = gauss_jordan(m)
#    if res:
#        return m[:,-1]
#    else:
#        raise Exception('Badly conditioned matrix')



with_cuda = (target=='gpu')

def solve_numba(A,Y, manual_upload=False):
    import time
    A = numpy.rollaxis(A,2,0)
    Y = numpy.rollaxis(Y,1,0)
    M = numpy.concatenate([A,Y[:,:,None]], axis=2)
    M = numpy.ascontiguousarray(M,dtype=dtype)
#    M  numpy.array(M,dtype=dtype)
    if with_cuda and manual_upload:
        M_cu = cuda.to_device(M)
        tt1 = time.time()
    #    X = gufunc(M)
        print(M_cu.__class__)
        print(M_cu.dtype)
        X_cu = solve(M_cu)
        print(X_cu.__class__)
        tt2 = time.time()
        X_cu.to_host()
        X = numpy.array( X_cu )
        print( X.__class__ )
        print('computation time: {}'.format(tt2-tt1))
    else:
        print('standard')
        print(M.shape)
        X = solve(M)
         
        print(X.__class__)

    print(X.shape)
    X = numpy.rollaxis(X,1,0)
    X = numpy.ascontiguousarray(X)
    return X


if __name__ == "__main__":
    import time
    K = 4
    A = numpy.array( numpy.random.random( (K,K)) , dtype=dtype )
    Y = numpy.array( numpy.random.random( K ), dtype=dtype ) 
    #X = solve(A,Y)
#    t1 = time.time()
#    for i in range(10):
#        mm = mms[i]
#        print(Y)
#        X = solve(A,Y)
#        print(X)
#        X = solve(A,Y)
#    t2 = time.time()
#    test = numpy.dot(A,X) - Y
#    print(X)
#    print('error : {}'.format(abs(test).max()))
#    print('elapsed : {}'.format(abs(t2-t1)))
#    exit()

    N = 100
    AA = numpy.random.random( (K,K,N) )
    YY = numpy.random.random( (K,N) )


    t1 = time.time()
    resp_numpy = solve_numpy(AA,YY)
    t2 = time.time()
    resp = solve_numba(AA,YY)
#    resp = gufunc(mm)
    t3 = time.time()
    print('error')
    print( abs(resp - resp_numpy).max() )
    print('time (numpy) : {}'.format(t2-t1))
    print('time (numba) : {}'.format(t3-t2))

    print(resp_numpy.shape)
    print(resp.shape)
    from dolo.numeric.serial_operations import serial_multiplication
    test1 = serial_multiplication(AA,resp_numpy[:,None,:]) - YY[:,None,:]
    test2 = serial_multiplication(AA,resp[:,None,:]) - YY[:,None,:]
    print('error (numpy) : {}'.format(abs(test1).max()))
    print('error (numba) : {}'.format(abs(test2).max()))
    exit()

    print('my')
    print(mm[0,:,-1])
    print('my 2')
    print(resp[0,:])
    print('true')
    print(numpy.linalg.solve(AA[0,:,:],YY[0,:]))
    exit()
    t =  gufunc2(AA,sol) 
    test = t - YY
    print('error : {}'.format(abs(test).max()))

    
    print('error : {}'.format(abs(numpy.dot(AA[0,:,:], sol[0,:])-YY[0,:]).max()))
    gufunc(AA,YY)

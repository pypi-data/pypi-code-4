


import lotus_core_hpp



class Wrapper4Lapack:

  def __init__(self):
    import platform
    if platform.system()=='Darwin':
      self.default_path="/usr/lib/liblapack.dylib"
    else:
      self.default_path="/usr/lib/liblapack.so"


  def get_liblapack(self, in_path):
    import ctypes

    path=in_path
    if path=="default":
      path=self.default_path
    if path=="autofind":
      import ctypes.util
      path=ctypes.util.find_library("lapack")
      if path==None:
        print "ERROR: fail in auto-find lapack library"
        quit()

    try:
      liblapack = ctypes.CDLL(path)
    except:
      print " ERROR: wrapper4lapack.inveser() can not find shared-type lapack library on the path:",path
      print "        please give appropriate library path and environment variables for lapack."
      quit()
    return liblapack
                             

  def inverse(self, m, path="default"):
    import ctypes
    liblapack = self.get_liblapack(path)

    I = m.get_I()
    J = m.get_J()
    lwork=4*I
    c_I     = ctypes.byref( ctypes.c_int(I) )
    c_J     = ctypes.byref( ctypes.c_int(J) )
    c_lda   = ctypes.byref( ctypes.c_int(I) )
    c_lwork = ctypes.byref( ctypes.c_int(lwork) )
    c_ipiv  = ctypes.byref( (ctypes.c_int*I)() )
    c_work  = ctypes.byref( (ctypes.c_double*lwork)() )
    c_info  = ctypes.c_int(0)
    c_mat   = (ctypes.c_double*(I*J))()
    for i in range(I):
      for j in range(J):
        c_mat[j*I+i]=m.get_value(i,j)

    liblapack.dgetrf_(c_I, c_J, ctypes.byref(c_mat), c_lda, c_ipiv, ctypes.byref(c_info))
    if c_info.value!=0:
      print "ERROR info=",c_info.value," in dgetrf of wrapper4lapack.inverse() "
      quit()

    liblapack.dgetri_(c_I, ctypes.byref(c_mat), c_lda, c_ipiv, \
                      c_work, c_lwork, ctypes.byref(c_info))
    if c_info.value!=0:
      print "ERROR info=",c_info.value," in dgetri of wrapper4lapack.inverse() "
      quit()

    for i in range(I):
      for j in range(J):
        tmp_v = c_mat[j*I+i]
        m.set_value(i,j, tmp_v)


  def dgesv(self, A, X, B, path="default"):
    import ctypes
    liblapack = self.get_liblapack(path)

    N    = A.get_I()
    nrhs = B.get_J()
    c_N     = ctypes.byref( ctypes.c_int(N) )
    c_nrhs  = ctypes.byref( ctypes.c_int(nrhs) )
    c_lda   = ctypes.byref( ctypes.c_int(N) )
    c_ldb   = ctypes.byref( ctypes.c_int(N) )
    c_ipiv  = ctypes.byref( (ctypes.c_int*N)() )
    c_info  = ctypes.c_int(0)
    c_mat_A = (ctypes.c_double*(N*N))()
    c_mat_B = (ctypes.c_double*(N*nrhs))()

    for i in range(N):
      for j in range(N):
        c_mat_A[j*N+i]=A.get_value(i,j)

    for i in range(N):
      for j in range(nrhs):
        c_mat_B[j*N+i]=B.get_value(i,j)

    liblapack.dgesv_(c_N, c_nrhs, ctypes.byref(c_mat_A), c_lda, c_ipiv, \
                     ctypes.byref(c_mat_B), c_ldb, ctypes.byref(c_info))

    if c_info.value!=0:
      print "ERROR info=",c_info.value," in dgesv "
      quit()

    X.set_IJ(N, nrhs)
    for i in range(N):
      for j in range(nrhs):
        X.set_value(i,j, c_mat_B[j*N+i])

    return c_info.value


  # A X = lamda X , calculate eigen value and eigen vector
  def dsyev(self, A, X, lamda, path="default"):
    import ctypes
    liblapack = self.get_liblapack(path)

    N     = A.get_I()
    lwork = N*4 
    c_jobz  = ctypes.byref( ctypes.c_char('V') )
    c_uplo  = ctypes.byref( ctypes.c_char('U') )
    c_N     = ctypes.byref( ctypes.c_int(N) )
    c_lda   = ctypes.byref( ctypes.c_int(N) )
    c_lwork = ctypes.byref( ctypes.c_int(lwork) )
    c_ipiv  = ctypes.byref( (ctypes.c_int*N)() )
    c_work  = ctypes.byref( (ctypes.c_double*lwork)() )

    c_info  = ctypes.c_int(0)
    c_lamda = (ctypes.c_double*(N))()
    c_mat_X = (ctypes.c_double*(N*N))()

    for i in range(N):
      for j in range(N):
        c_mat_X[j*N+i]=A.get_value(i,j)

    liblapack.dsyev_(c_jobz, c_uplo, c_N, ctypes.byref(c_mat_X), c_lda, c_lamda, \
                     c_work, c_lwork, ctypes.byref(c_info))
    if c_info.value!=0:
      print "ERROR info=",c_info.value," in lapack_dsyev "
      quit()

    X.set_IJ(N, N)
    lotus_core_hpp.vector_clear(lamda)
    for i in range(N):
      lamda.append(c_lamda[i])
      for j in range(N):
        X.set_value(i, j, c_mat_X[j*N+i])

    return c_info.value


  # A X = lamda S X , calcualte eigen value and eigen vector
  def dsygv(self, A, S, X, lamda, path="default"):
    import ctypes
    liblapack = self.get_liblapack(path)

    N     = A.get_I()
    lwork = N*4 
    c_itype = ctypes.byref( ctypes.c_int(1) )
    c_jobz  = ctypes.byref( ctypes.c_char('V') )
    c_uplo  = ctypes.byref( ctypes.c_char('U') )
    c_N     = ctypes.byref( ctypes.c_int(N) )
    c_lda   = ctypes.byref( ctypes.c_int(N) )
    c_ldb   = ctypes.byref( ctypes.c_int(N) )
    c_lwork = ctypes.byref( ctypes.c_int(lwork) )
    c_ipiv  = ctypes.byref( (ctypes.c_int*N)() )
    c_work  = ctypes.byref( (ctypes.c_double*lwork)() )

    c_info  = ctypes.c_int(0)
    c_lamda = (ctypes.c_double*(N))()
    c_mat_X = (ctypes.c_double*(N*N))()
    c_mat_S = (ctypes.c_double*(N*N))()

    for i in range(N):
      for j in range(N):
        c_mat_X[j*N+i]=A.get_value(i,j)
        c_mat_S[j*N+i]=S.get_value(i,j)

    liblapack.dsygv_(c_itype, c_jobz, c_uplo, c_N, ctypes.byref(c_mat_X), c_lda, \
                     ctypes.byref(c_mat_S), c_ldb, c_lamda, c_work, c_lwork, ctypes.byref(c_info))
                    
    if c_info.value!=0:
      print "ERROR info=",c_info.value," in lapack_dsygv "
      quit()

    X.set_IJ(N, N)
    lotus_core_hpp.vector_clear(lamda)
    for i in range(N):
      lamda.append(c_lamda[i])
      for j in range(N):
        X.set_value(i, j, c_mat_X[j*N+i])

    return c_info.value






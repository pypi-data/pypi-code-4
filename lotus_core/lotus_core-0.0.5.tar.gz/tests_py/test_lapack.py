
import unittest
import lotus_core
import lotus_core_hpp
import math
import os


def check_M(A, X, lamda):
  N_cgtos = len(lamda)
  Ax = lotus_core_hpp.get_vector_double(N_cgtos)

  abs_error=0.0
  for q in range(N_cgtos):
    for i in range(N_cgtos):
      tmp_v_i = 0.0
      for j in range(N_cgtos):
        tmp_v_i += A.get_value(i,j)*X.get_value(j,q)
      Ax[i]=tmp_v_i

    for i in range(N_cgtos):
      tmp_c = Ax[i] - lamda[q]*X.get_value(i,q)
      abs_error += abs(tmp_c)
  
  return abs_error



def check_M2(A, S, X, lamda, SX):
  N_cgtos = len(lamda)
  Ax = []
  [Ax.append(0.0) for i in range(N_cgtos)]
  SX.set_IJ(N_cgtos, N_cgtos)
  lotus_core_hpp.mat_mul(SX, S, X)

  abs_error=0.0
  for q in range(N_cgtos):
    for i in range(N_cgtos):
      tmp_v_i = 0.0
      for j in range(N_cgtos):
        tmp_v_i += A.get_value(i,j)*X.get_value(j,q)
      Ax[i]=tmp_v_i

    for i in range(N_cgtos):
      tmp_c = Ax[i] - lamda[q]*SX.get_value(i,q)
      abs_error += abs(tmp_c)
  
  return abs_error


def td_lapack_base(filename, mode, mode_mat):

  if mode_mat==0:
    lts    = lotus_core.create_lotus()
    H_core = lotus_core_hpp.dMatrix()
    S      = lotus_core_hpp.dMatrix()
    inv_S  = lotus_core_hpp.dMatrix()
    M      = lotus_core_hpp.dMatrix()
    M2     = lotus_core_hpp.dMatrix()
    SX     = lotus_core_hpp.dMatrix()
    X      = lotus_core_hpp.dMatrix()
    X2     = lotus_core_hpp.dMatrix()
  if mode_mat==1:
    lts    = lotus_core.create_lotus("dMatrix_map")
    H_core = lotus_core_hpp.dMatrix_map()
    S      = lotus_core_hpp.dMatrix_map()
    inv_S  = lotus_core_hpp.dMatrix_map()
    M      = lotus_core_hpp.dMatrix_map()
    M2     = lotus_core_hpp.dMatrix_map()
    SX     = lotus_core_hpp.dMatrix_map()
    X      = lotus_core_hpp.dMatrix_map()
    X2     = lotus_core_hpp.dMatrix_map()

  lamda  = lotus_core_hpp.get_vector_double()
  lamda2 = lotus_core_hpp.get_vector_double()

  lts.read_in_file(filename)
  lts.cal_matrix("H_core", H_core)
  lts.cal_matrix("S",      S)

  ret=0
  abs_error=1.0e-11

  if mode==0:
    lts.cal_matrix("S", inv_S)
    lotus_core.Wrapper4Lapack().inverse(inv_S)
    I=S.get_I()
    M.set_IJ(I,I)
    lotus_core_hpp.mat_mul(M, S, inv_S)
    for i in range(I):
      for j in range(I):
        if i==j:
          if abs(M.get_value(i,j)-1.0)>abs_error: ret=1
        else:
          if abs(M.get_value(i,j)-0.0)>abs_error: ret=1
    lotus_core_hpp.mat_mul(M, inv_S, S)
    for i in range(I):
      for j in range(I):
        if i==j:
          if abs(M.get_value(i,j)-1.0)>abs_error: ret=1
        else:
          if abs(M.get_value(i,j)-0.0)>abs_error: ret=1

  if mode==1:
    I=S.get_I()
    M.set_IJ(I,I/2)
    for i in range(I):
      for j in range(I/2):
        M.set_value(i,j, S.get_value(i,j))

    lotus_core.Wrapper4Lapack().dgesv(H_core, X, M)

    lts.cal_matrix("H_core", M2)
    lotus_core.Wrapper4Lapack().inverse(M2)
    lotus_core_hpp.mat_mul(M2, M2, M) 
    
    for i in range(I):
      for j in range(I/2):
        if abs(X.get_value(i,j)-M2.get_value(i,j))>abs_error:
          ret=1

  if mode==2:
    lotus_core_hpp.cal_eigen(H_core, X, lamda)
    lotus_core.Wrapper4Lapack().dsyev(H_core, X2, lamda2)
    I=X.get_I()
    check=check_M(H_core, X, lamda)
    if check>abs_error:    ret=1
    check=check_M(H_core, X2, lamda2)
    if check>abs_error:  ret=1
    for i in range(I):
      if abs(lamda[i]-lamda2[i])>abs_error:
        print "   ERROR i=",i,"lamda",lamda[i],lamda2[i],"diff",lamda[i]-lamda2[i]
        ret=1

  if mode==3:
    lotus_core_hpp.cal_eigen(H_core, S, X, lamda)
    lotus_core.Wrapper4Lapack().dsygv(H_core, S, X2, lamda2)
    I=X.get_I()
    check=check_M2(H_core, S, X, lamda, SX)
    if check>abs_error:    ret=1
    check=check_M2(H_core, S, X2, lamda2, SX)
    if check>abs_error:  ret=1
    for i in range(I):
      if abs(lamda[i]-lamda2[i])>abs_error:
        print "   ERROR i=",i,"lamda",lamda[i],lamda2[i],"diff",lamda[i]-lamda2[i]
        ret=1

  return ret 


class td_lapack(unittest.TestCase):
  
  def setUp(self):
    pass

  def test_inverse(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_inverse ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_6-31g.in"
    check = td_lapack_base(filename, 0, 0) 
    self.assertEqual(check, 0)
    check = td_lapack_base(filename, 0, 1) 
    self.assertEqual(check, 0)


  def test_dgesv(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dgesv ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_6-31g.in"
    check = td_lapack_base(filename, 1, 0) 
    self.assertEqual(check, 0)
    check = td_lapack_base(filename, 1, 1) 
    self.assertEqual(check, 0)


  def test_dsyev(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dsyev ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_6-31g.in"
    check = td_lapack_base(filename, 2, 0) 
    self.assertEqual(check, 0)
    check = td_lapack_base(filename, 2, 1) 
    self.assertEqual(check, 0)

  def test_dsygv(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dsygv ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_6-31g.in"
    check = td_lapack_base(filename, 3, 0) 
    self.assertEqual(check, 0)
    check = td_lapack_base(filename, 3, 1) 
    self.assertEqual(check, 0)




if __name__ == "__main__":
  try:
    from mpi4py import MPI
  except:
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"
  lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()

  unittest.main()


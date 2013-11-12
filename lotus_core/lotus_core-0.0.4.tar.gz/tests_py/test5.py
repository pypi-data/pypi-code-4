
import unittest
import lotus_core_hpp
import lotus_core
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


def td_matrix_base(filename, exact_v, mode_mat):
  lamda = lotus_core_hpp.get_vector_double()

  if mode_mat==0:
    fock1e  = lotus_core_hpp.Fock1e()
    lotus   = lotus_core.create_lotus("dMatrix")
    S       = lotus_core_hpp.dMatrix()
    X       = lotus_core_hpp.dMatrix()
    SX      = lotus_core_hpp.dMatrix()
    H_core  = lotus_core_hpp.dMatrix()
    zS      = lotus_core_hpp.zMatrix()
    zX      = lotus_core_hpp.zMatrix()
    zH_core = lotus_core_hpp.zMatrix()
    zSX     = lotus_core_hpp.zMatrix()
  elif mode_mat==1:
    fock1e  = lotus_core_hpp.Fock1e_map()
    lotus   = lotus_core.create_lotus("dMatrix_map")
    S       = lotus_core_hpp.dMatrix_map()
    X       = lotus_core_hpp.dMatrix_map()
    SX      = lotus_core_hpp.dMatrix_map()
    H_core  = lotus_core_hpp.dMatrix_map()
    zS      = lotus_core_hpp.zMatrix_map()
    zX      = lotus_core_hpp.zMatrix_map()
    zH_core = lotus_core_hpp.zMatrix_map()
    zSX     = lotus_core_hpp.zMatrix_map()
  
  
  check_v = lotus_core_hpp.get_vector_double(10)
  process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
  if process_num==0: print type(S)

  lotus.read_in_file(filename)
  
  lotus.cal_matrix("S", S)
  lotus.cal_matrix("H_core", H_core)

  lotus_core_hpp.mat_copy(zS, S) 
  lotus_core_hpp.mat_copy(zH_core, H_core) 

  lotus_core_hpp.cal_eigen(H_core, X, lamda)
  check_v[0] = check_M(H_core, X, lamda)

  lotus_core_hpp.cal_z_eigen(zH_core, zX, lamda)
  check_v[1] = check_M(H_core, X, lamda)

  lotus_core_hpp.cal_eigen(H_core, S, X, lamda)
  check_v[2] = check_M2(H_core, S, X, lamda, SX)

  lotus_core_hpp.cal_z_eigen(zH_core, zS, zX, lamda)
  check_v[3] = check_M2(zH_core, zS, zX, lamda, zSX)

  ret=0
  abs_error=5.0e-11
  if abs( check_v[0]-exact_v[0])>abs_error or abs(check_v[1]-exact_v[1])>abs_error or \
     abs( check_v[0]-exact_v[0])>abs_error or abs(check_v[1]-exact_v[1])>abs_error:
    ret=1
    print " ----- in td_matrix_base -----"
    print "   exact_v[0]",exact_v[0],"check_v[0]",check_v[0],"diff",exact_v[0]-check_v[0]
    print "   exact_v[1]",exact_v[1],"check_v[1]",check_v[1],"diff",exact_v[1]-check_v[1]
    print "   exact_v[2]",exact_v[2],"check_v[2]",check_v[2],"diff",exact_v[2]-check_v[2]
    print "   exact_v[3]",exact_v[3],"check_v[3]",check_v[3],"diff",exact_v[3]-check_v[3]

  return ret



class td_matrix(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def test_matrix(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_matrix ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_6-31gs.in"
    exact_v = lotus_core_hpp.get_vector_double(10)
    check = td_matrix_base(filename, exact_v, 0)
    self.assertEqual(check, 0)
    check = td_matrix_base(filename, exact_v, 1)
    self.assertEqual(check, 0)



if __name__ == "__main__":
  try:
    from mpi4py import MPI
  except:
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"
  lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()

  unittest.main()



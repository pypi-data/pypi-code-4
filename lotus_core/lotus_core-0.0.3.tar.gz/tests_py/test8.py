

import unittest
import lotus_core_hpp
import lotus_core
import math
import os


def td_lotus_base(filename, exact_v, mode, sel_functor, mode_mat):

  if mode_mat==0:
    lts     = lotus_core.create_lotus("dMatrix")
    S       = lotus_core_hpp.dMatrix()
    M       = lotus_core_hpp.dMatrix()
  if mode_mat==1:
    lts     = lotus_core.create_lotus("dMatrix_map")
    S       = lotus_core_hpp.dMatrix_map()
    M       = lotus_core_hpp.dMatrix_map()

  os.chdir( os.path.abspath(os.path.dirname(__file__)) )

  lts.read_in_file_debug(filename)
  lts.cal_matrix("S", S)
  lts.guess_h_core()

  check_v = lotus_core_hpp.get_vector_double(10)
  abs_error=1.0e-8
  if mode==0:
    check_v[0] = lts.get_N_cgtos() 
    check_v[1] = lts.get_N_ecps() 
    check_v[2] = lts.get_N_atoms() 
    lts.cal_matrix("K", M)
    check_v[3] = lotus_core_hpp.Util.cal_DV(S, M)
    lts.cal_matrix("NA", M)
    check_v[4] = lotus_core_hpp.Util.cal_DV(S, M)
    lts.cal_matrix("ECP", M)
    check_v[5] = lotus_core_hpp.Util.cal_DV(S, M)
    lts.cal_matrix("H_core", M)
    check_v[6] = lotus_core_hpp.Util.cal_DV(S, M)
    lts.cal_matrix("D", M)
    check_v[7] = lotus_core_hpp.Util.cal_DV(S, M)
    lts.cal_matrix("D_a", M)
    check_v[8] = lotus_core_hpp.Util.cal_DV(S, M)

  ret=0
  abs_error=5.0e-11
  if abs( check_v[0]-exact_v[0])>abs_error or abs(check_v[1]-exact_v[1])>abs_error or \
     abs( check_v[2]-exact_v[2])>abs_error or abs(check_v[3]-exact_v[3])>abs_error or \
     abs( check_v[4]-exact_v[4])>abs_error or abs(check_v[5]-exact_v[5])>abs_error or \
     abs( check_v[6]-exact_v[6])>abs_error or abs(check_v[7]-exact_v[7])>abs_error or \
     abs( check_v[8]-exact_v[8])>abs_error:
    ret=1
    print " ----- in td_lotus_base -----"
    print "   exact_v[0]",exact_v[0],"check_v[0]",check_v[0],"diff",exact_v[0]-check_v[0]
    print "   exact_v[1]",exact_v[1],"check_v[1]",check_v[1],"diff",exact_v[1]-check_v[1]
    print "   exact_v[2]",exact_v[2],"check_v[2]",check_v[2],"diff",exact_v[2]-check_v[2]
    print "   exact_v[3]",exact_v[3],"check_v[3]",check_v[3],"diff",exact_v[3]-check_v[3]
    print "   exact_v[4]",exact_v[4],"check_v[4]",check_v[4],"diff",exact_v[4]-check_v[4]
    print "   exact_v[5]",exact_v[5],"check_v[5]",check_v[5],"diff",exact_v[5]-check_v[5]
    print "   exact_v[6]",exact_v[6],"check_v[6]",check_v[6],"diff",exact_v[6]-check_v[6]
    print "   exact_v[7]",exact_v[7],"check_v[7]",check_v[7],"diff",exact_v[7]-check_v[7]
    print "   exact_v[8]",exact_v[8],"check_v[8]",check_v[8],"diff",exact_v[8]-check_v[8]

  return ret


class td_lotus(unittest.TestCase):
  
  def setUp(self):
    pass

  def test_lotus(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_lotus_matrix ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d_for_debug.in"
    exact_v = lotus_core_hpp.get_vector_double(10)
    exact_v[0] =  12.0
    exact_v[1] =   2.0
    exact_v[2] =   3.0
    exact_v[3] =  35.305943879326982
    exact_v[4] =-120.209150645409
    exact_v[5] =   1.64195529039806
    exact_v[6] = -83.2612514756841
    exact_v[7] =   4.0
    exact_v[8] =   4.0
    check = td_lotus_base(filename, exact_v, 0, 0, 0) 
    self.assertEqual(check, 0)


if __name__ == "__main__":
  try:
    from mpi4py import MPI
  except:
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"
  lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()

  unittest.main()


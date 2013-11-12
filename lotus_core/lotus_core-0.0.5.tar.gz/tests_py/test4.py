
import unittest
import lotus_core_hpp
import math
import os


def td_dft_pbc_mat_base(filename, exact_v, mode, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  ecps   = lotus_core_hpp.ECP.get_ecps_from_file(filename)

  ctrl_pbc = lotus_core_hpp.CTRL_PBC()
  T123 = lotus_core_hpp.get_vector_double(9)
  T123[0] =  1.0 
  T123[1] = -0.5 
  T123[2] =  0.0 
  T123[3] =  0.0 
  T123[4] = -1.5 
  T123[5] =  0.0 
  T123[6] =  0.0 
  T123[7] =  1.5 
  T123[8] =  1.0 
  max_Nc = lotus_core_hpp.get_vector_int(3)
  ctrl_pbc.set_T123(T123)
#  ctrl_pbc.show()
  
  if mode_mat==0:
    fock1e = lotus_core_hpp.Fock1e()
    ginteg = lotus_core_hpp.Grid_Inte()
    S_PBC  = lotus_core_hpp.get_vector_dMatrix()
    M_PBC  = lotus_core_hpp.get_vector_dMatrix()
  elif mode_mat==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    ginteg = lotus_core_hpp.Grid_Inte_map()
    S_PBC  = lotus_core_hpp.get_vector_dMatrix_map()
    M_PBC  = lotus_core_hpp.get_vector_dMatrix_map()

#  print "*********** DEBUG mode_mat=",mode_mat," type ",type(ginteg), type(M_PBC)

  if mode==0:  functor = lotus_core_hpp.Slater_Functor()
  if mode==1:  functor = lotus_core_hpp.B88_Functor()
  if mode==2:  functor = lotus_core_hpp.SVWN_Functor()
  if mode==3:  functor = lotus_core_hpp.BLYP_Functor()
  if mode==4:  functor = lotus_core_hpp.B3LYP_Functor()

  check_v = lotus_core_hpp.get_vector_double(10)

  max_Nc[0] = 0
  max_Nc[1] = 0
  max_Nc[2] = 0
  ctrl_pbc.set_max_Nc(max_Nc)
  fock1e.cal_S_PBC(S_PBC, scgtos, ctrl_pbc)
  check_v[0] = ginteg.grid_integral_mat_PBC(M_PBC, S_PBC, scgtos, ctrl_pbc, functor)
  check_v[1] = lotus_core_hpp.Util_PBC.cal_DV(M_PBC, S_PBC, ctrl_pbc.get_N123_c() ) 

  max_Nc[0] = 1
  max_Nc[1] = 0
  max_Nc[2] = 0
  ctrl_pbc.set_max_Nc(max_Nc)
  fock1e.cal_S_PBC(S_PBC, scgtos, ctrl_pbc)
  check_v[2] = ginteg.grid_integral_mat_PBC(M_PBC, S_PBC, scgtos, ctrl_pbc, functor)
  check_v[3] = lotus_core_hpp.Util_PBC.cal_DV(M_PBC, S_PBC, ctrl_pbc.get_N123_c() ) 

  max_Nc[0] = 1
  max_Nc[1] = 1
  max_Nc[2] = 0
  ctrl_pbc.set_max_Nc(max_Nc)
  fock1e.cal_S_PBC(S_PBC, scgtos, ctrl_pbc)
  check_v[4] = ginteg.grid_integral_mat_PBC(M_PBC, S_PBC, scgtos, ctrl_pbc, functor)
  check_v[5] = lotus_core_hpp.Util_PBC.cal_DV(M_PBC, S_PBC, ctrl_pbc.get_N123_c() ) 

  max_Nc[0] = 1
  max_Nc[1] = 1
  max_Nc[2] = 1
  ctrl_pbc.set_max_Nc(max_Nc)
  fock1e.cal_S_PBC(S_PBC, scgtos, ctrl_pbc)
  check_v[6] = ginteg.grid_integral_mat_PBC(M_PBC, S_PBC, scgtos, ctrl_pbc, functor)
  check_v[7] = lotus_core_hpp.Util_PBC.cal_DV(M_PBC, S_PBC, ctrl_pbc.get_N123_c() ) 

  max_Nc[0] = 0
  max_Nc[1] = 2
  max_Nc[2] = 2
  ctrl_pbc.set_max_Nc(max_Nc)
  fock1e.cal_S_PBC(S_PBC, scgtos, ctrl_pbc)
  check_v[8] = ginteg.grid_integral_mat_PBC(M_PBC, S_PBC, scgtos, ctrl_pbc, functor)
  check_v[9] = lotus_core_hpp.Util_PBC.cal_DV(M_PBC, S_PBC, ctrl_pbc.get_N123_c() ) 

  ret=0
  abs_error=1.0e-9
  if math.fabs( check_v[0] - exact_v[0])>abs_error or math.fabs( check_v[1] - exact_v[1] )>abs_error or \
     math.fabs( check_v[2] - exact_v[2])>abs_error or math.fabs( check_v[3] - exact_v[3] )>abs_error or \
     math.fabs( check_v[4] - exact_v[4])>abs_error or math.fabs( check_v[5] - exact_v[5] )>abs_error or \
     math.fabs( check_v[6] - exact_v[6])>abs_error or math.fabs( check_v[7] - exact_v[7] )>abs_error or \
     math.fabs( check_v[8] - exact_v[8])>abs_error or math.fabs( check_v[9] - exact_v[9] )>abs_error:
    ret=1
    print " ----- in td_dft_mat_pbc_base -----"
    print "   exact_v[0]",exact_v[0],"check_v[0]",check_v[0],"diff",exact_v[0]-check_v[0]
    print "   exact_v[1]",exact_v[1],"check_v[1]",check_v[1],"diff",exact_v[1]-check_v[1]
    print "   exact_v[2]",exact_v[2],"check_v[2]",check_v[2],"diff",exact_v[2]-check_v[2]
    print "   exact_v[3]",exact_v[3],"check_v[3]",check_v[3],"diff",exact_v[3]-check_v[3]
    print "   exact_v[4]",exact_v[4],"check_v[4]",check_v[4],"diff",exact_v[4]-check_v[4]
    print "   exact_v[5]",exact_v[5],"check_v[5]",check_v[5],"diff",exact_v[5]-check_v[5]
    print "   exact_v[6]",exact_v[6],"check_v[6]",check_v[6],"diff",exact_v[6]-check_v[6]
    print "   exact_v[7]",exact_v[7],"check_v[7]",check_v[7],"diff",exact_v[7]-check_v[7]
    print "   exact_v[8]",exact_v[8],"check_v[8]",check_v[8],"diff",exact_v[8]-check_v[8]
    print "   exact_v[9]",exact_v[9],"check_v[9]",check_v[9],"diff",exact_v[9]-check_v[9]

  return ret



class td_dft_pbc(unittest.TestCase):
  
  def setUp(self):
    pass
  
  # slater
  def test_dft_pbc_mat_slater(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_pbc_mat_slater ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -8.68918462925892,
                -5.79278975283924,
               -27.9470595016986,
               -18.3924381013131,
               -68.2891368400923,
               -40.7319674149235,
              -247.966315093019,
              -138.684446232039,
               -66.701110932087,
               -44.9884398391664]
    check = td_dft_pbc_mat_base(filename, exact_v, 0, 0)
    self.assertEqual(check, 0)
    check = td_dft_pbc_mat_base(filename, exact_v, 0, 1)
    self.assertEqual(check, 0)

  # svwn
  def test_dft_pbc_mat_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_pbc_mat_svwn ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -32.0105268520034,
                -20.9500806637737,
               -118.27853809234,
                -73.9886286096848,
               -345.455974988649,
               -195.890365412771,
              -1259.35881653829,
               -674.86594442786,
               -360.996815911785,
               -240.620223087907]
    check = td_dft_pbc_mat_base(filename, exact_v, 2, 0)
    self.assertEqual(check, 0)
    check = td_dft_pbc_mat_base(filename, exact_v, 2, 1)
    self.assertEqual(check, 0)
  
  # blyp
  def test_dft_pbc_mat_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_pbc_mat_blyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -31.3144744951157,
                -20.4694869661198,
               -115.190027883041,
                -72.1824246518356,
               -336.759674739418,
               -191.604790643238,
              -1234.31848438909,
               -663.667927459116,
               -352.107236868374,
               -235.516086217432]
    check = td_dft_pbc_mat_base(filename, exact_v, 3, 0)
    self.assertEqual(check, 0)
    check = td_dft_pbc_mat_base(filename, exact_v, 3, 1)
    self.assertEqual(check, 0)
  
  # b3lyp
  def test_dft_pbc_mat_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_pbc_mat_b3lyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -25.6027334603965,
                -16.6908133737727,
                -93.6980535024515,
                -58.5599510952698,
               -272.91806864864,
               -154.938239837276,
               -996.492587711361,
               -534.829799499708,
               -285.197210945696,
               -190.333328397354]
    check = td_dft_pbc_mat_base(filename, exact_v, 4, 0)
    self.assertEqual(check, 0)
    check = td_dft_pbc_mat_base(filename, exact_v, 4, 1)
    self.assertEqual(check, 0)



if __name__ == "__main__":
  try:
    from mpi4py import MPI
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
  except:
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"

  unittest.main(exit=False)


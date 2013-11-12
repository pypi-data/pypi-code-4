
import unittest
import lotus_core_hpp
import math
import os

def td_fock1e_K_mat_base(filename, exact_v, mode):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  if mode==0:
    fock1e = lotus_core_hpp.Fock1e()
    S      = lotus_core_hpp.dMatrix()
    K      = lotus_core_hpp.dMatrix()
  elif mode==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    S      = lotus_core_hpp.dMatrix_map()
    K      = lotus_core_hpp.dMatrix_map()

  fock1e.cal_S(S, scgtos)
  fock1e.cal_K(K, scgtos)
  sk     = lotus_core_hpp.Util.cal_DV(S, K)

  abs_error=1.0e-8
  if math.fabs(sk - exact_v)<abs_error: ret=0
  else:          
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print "exact_v ",exact_v," sk ",sk," diff ",exact_v-sk      
    ret=1
 
  return ret


def td_fock1e_NA_mat_base(filename, exact_v, mode):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  if mode==0:
    fock1e = lotus_core_hpp.Fock1e()
    S      = lotus_core_hpp.dMatrix()
    NA     = lotus_core_hpp.dMatrix()
  elif mode==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    S      = lotus_core_hpp.dMatrix_map()
    NA     = lotus_core_hpp.dMatrix_map()

  charges    = lotus_core_hpp.get_vector_Charge(2)
  charges[0] = lotus_core_hpp.Charge(1, 0.1, 0.2, 0.3, 0)
  charges[1] = lotus_core_hpp.Charge(2, 1.0, 1.1, 1.2, 1)
  fock1e.cal_S(S, scgtos)
  fock1e.cal_NA(NA, scgtos, charges)

  sna     = lotus_core_hpp.Util.cal_DV(S, NA)

  abs_error=1.0e-8
  if math.fabs(sna - exact_v)<abs_error: ret=0
  else:          
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print "exact_v ",exact_v," sna ",sna," diff ",exact_v-sna     
    ret=1
 
  return ret



def td_fock1e_ECP_mat_base(filename, exact_v, mode):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  ecps   = lotus_core_hpp.ECP.get_ecps_from_file(filename)
  if mode==0:
    fock1e = lotus_core_hpp.Fock1e()
    cecp   = lotus_core_hpp.ECP_matrix()
    S      = lotus_core_hpp.dMatrix()
    M_ecp  = lotus_core_hpp.dMatrix()
  elif mode==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    cecp   = lotus_core_hpp.ECP_matrix_map()
    S      = lotus_core_hpp.dMatrix_map()
    M_ecp  = lotus_core_hpp.dMatrix_map()

  fock1e.cal_S(S, scgtos)
  cecp.cal_ECP(M_ecp, scgtos, ecps)
  secp     = lotus_core_hpp.Util.cal_DV(S, M_ecp)

  abs_error=1.0e-8
  if math.fabs(secp - exact_v)<abs_error: ret=0
  else:          
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print "exact_v ",exact_v," secp ",secp," diff ",exact_v-secp      
    ret=1
 
  return ret


def td_fock1e_grad_base(filename, exact_v, mode, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  ecps   = lotus_core_hpp.ECP.get_ecps_from_file(filename)
  if mode_mat==0:
    fock1e = lotus_core_hpp.Fock1e()
    cecp   = lotus_core_hpp.ECP_matrix()
    S      = lotus_core_hpp.dMatrix()
  elif mode_mat==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    cecp   = lotus_core_hpp.ECP_matrix_map()
    S      = lotus_core_hpp.dMatrix_map()

  charges    = lotus_core_hpp.get_vector_Charge(2)
  charges[0] = lotus_core_hpp.Charge(1, 0.1, 0.2, 0.3, 0)
  charges[1] = lotus_core_hpp.Charge(2, 1.0, 1.1, 1.2, 1)
  fock1e.cal_S(S, scgtos)

  if mode==0:  grad = fock1e.cal_grad_S(scgtos, S)
  if mode==1:  grad = fock1e.cal_grad_K(scgtos, S)
  if mode==2:  grad = fock1e.cal_grad_NA(scgtos, S, charges)
  if mode==3:  grad = cecp.cal_grad_ECP(scgtos, ecps, S)

  check_v=[0.0 for i in range(3)]
  for a in range( len(grad)/3 ):
    check_v[0] += math.sqrt(grad[a*3+0]*grad[a*3+0])
    check_v[1] += math.sqrt(grad[a*3+1]*grad[a*3+1])
    check_v[2] += math.sqrt(grad[a*3+2]*grad[a*3+2])

  ret=0
  if math.fabs(check_v[0] - exact_v[0])>1.0e-13 or \
     math.fabs(check_v[1] - exact_v[1])>1.0e-13 or \
     math.fabs(check_v[2] - exact_v[2])>1.0e-13:
    ret=1
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print " ----- error in td_fock1e_grad_base -----"
      print "exact_v[0] ",exact_v[0],"check_v[0]",check_v[0],"diff",exact_v[0]-check_v[0]   
      print "exact_v[1] ",exact_v[1],"check_v[1]",check_v[1],"diff",exact_v[1]-check_v[1]   
      print "exact_v[2] ",exact_v[2],"check_v[2]",check_v[2],"diff",exact_v[0]-check_v[2]   

  return ret



def td_fock1e_pbc_base(filename, exact_v, mode, mode_mat):
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
  max_Nc[0] = 1
  max_Nc[1] = 2
  max_Nc[2] = 1
  max_Nt = lotus_core_hpp.get_vector_int(3)
  max_Nt[0] = 2
  max_Nt[1] = 2
  max_Nt[2] = 2
  ctrl_pbc.set_T123(T123)
  ctrl_pbc.set_max_Nc(max_Nc)
  ctrl_pbc.set_max_Nt(max_Nt)
#  ctrl_pbc.show()
  
  if mode_mat==0:
    fock1e = lotus_core_hpp.Fock1e()
    cecp   = lotus_core_hpp.ECP_matrix()
    S_PBC  = lotus_core_hpp.get_vector_dMatrix()
    M_PBC  = lotus_core_hpp.get_vector_dMatrix()
  elif mode_mat==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    cecp   = lotus_core_hpp.ECP_matrix_map()
    S_PBC  = lotus_core_hpp.get_vector_dMatrix_map()
    M_PBC  = lotus_core_hpp.get_vector_dMatrix_map()

  charges    = lotus_core_hpp.get_vector_Charge(2)
  charges[0] = lotus_core_hpp.Charge(1, 0.1, 0.2, 0.3, 0)
  charges[1] = lotus_core_hpp.Charge(2, 1.0, 1.1, 1.2, 1)
  fock1e.cal_S_PBC(S_PBC, scgtos, ctrl_pbc)

  if mode==0:  fock1e.cal_K_PBC(M_PBC, scgtos, ctrl_pbc)
  if mode==1:  fock1e.cal_NA_PBC(M_PBC, scgtos, charges, ctrl_pbc)
  if mode==2:  cecp.cal_ECP_PBC(M_PBC, scgtos, ecps, ctrl_pbc)

  N123_c = ctrl_pbc.get_N123_c()
  check_v = lotus_core_hpp.Util_PBC.cal_DV(S_PBC, M_PBC, N123_c)

  ret=0
  if math.fabs(check_v - exact_v)>1.0e-10:
    ret=1
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0:
      print " ----- error in td_fock1e_pbc_base -----"
      print "exact_v[0] ",exact_v,"check_v",check_v,"diff",exact_v-check_v   

  return ret






class td_fock1e(unittest.TestCase):
  
  def setUp(self):
    pass

  def test_k(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_k ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    check = td_fock1e_K_mat_base(filename,        15.209924623687, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_K_mat_base(filename,        15.209924623687, 1) 
    self.assertEqual(check, 0)

  def test_k_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_k_plus_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    check = td_fock1e_K_mat_base(filename, 35.305943879327, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_K_mat_base(filename, 35.305943879327, 1) 
    self.assertEqual(check, 0)

  def test_na(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_na ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    check = td_fock1e_NA_mat_base(filename,        -14.6450507433424, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_NA_mat_base(filename,        -14.6450507433424, 1) 
    self.assertEqual(check, 0)

  def test_na_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_na_plus_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    check = td_fock1e_NA_mat_base(filename, -35.5342442165267, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_NA_mat_base(filename, -35.5342442165267, 1) 
    self.assertEqual(check, 0)

  def test_ecp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_ecp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    check = td_fock1e_ECP_mat_base(filename,         0.668115104438203, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_ECP_mat_base(filename,         0.668115104438203, 1) 
    self.assertEqual(check, 0)

  def test_ecp_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_ecp_plus_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    check = td_fock1e_ECP_mat_base(filename,  1.64195529039806, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_ECP_mat_base(filename,  1.64195529039806, 1) 
    self.assertEqual(check, 0)

  def test_grad_s(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_s ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v=[0.797858610874905,
             0.000000000000000,
             1.19156682184131]
    check = td_fock1e_grad_base(filename,        exact_v, 0, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename,        exact_v, 0, 1) 
    self.assertEqual(check, 0)

  def test_grad_s_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_s_plus_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v=[1.76573600226019,
             0.00000000000000,
             2.55888122805177]
    check = td_fock1e_grad_base(filename, exact_v, 0, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename, exact_v, 0, 1) 
    self.assertEqual(check, 0)

  def test_grad_k(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_k ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v=[1.25963801096052,
             0.00000000000000,
             1.91082703634836]
    check = td_fock1e_grad_base(filename,        exact_v, 1, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename,        exact_v, 1, 1) 
    self.assertEqual(check, 0)

  def test_grad_k_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_k_plus_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v=[3.20462307132361,
             0.00000000000000,
             4.67643987627959]
    check = td_fock1e_grad_base(filename, exact_v, 1, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename, exact_v, 1, 1) 
    self.assertEqual(check, 0)

  def test_grad_na(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_na ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v=[3.89035924054393,
             5.48287225486067,
             6.43108061233738]
    check = td_fock1e_grad_base(filename,        exact_v, 2, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename,        exact_v, 2, 1) 
    self.assertEqual(check, 0)

  def test_grad_na_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_na_plus_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v=[ 9.73663174932849,
             12.7737287310335,
             16.1902064506491]
    check = td_fock1e_grad_base(filename, exact_v, 2, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename, exact_v, 2, 1) 
    self.assertEqual(check, 0)

  def test_grad_ecp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_ecp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v=[0.435739119392969,
             0.000000000000000,
             0.657556467625155]
    check = td_fock1e_grad_base(filename,        exact_v, 3, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename,        exact_v, 3, 1) 
    self.assertEqual(check, 0)

  def test_grad_ecp_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_ecp_plus_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v=[0.581764645449941,
             0.000000000000000,
             0.877934978556851]
    check = td_fock1e_grad_base(filename, exact_v, 3, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_grad_base(filename, exact_v, 3, 1) 
    self.assertEqual(check, 0)

  def test_pbc_k(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_pbc_k ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = 57.266002474008
    check = td_fock1e_pbc_base(filename,        exact_v, 0, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_pbc_base(filename,        exact_v, 0, 1) 
    self.assertEqual(check, 0)

  def test_pbc_k_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_pbc_k ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = 202.146619381262
    check = td_fock1e_pbc_base(filename, exact_v, 0, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_pbc_base(filename, exact_v, 0, 1) 
    self.assertEqual(check, 0)

  def test_pbc_na(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_pbc_na ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = -4711.62478666429
    check = td_fock1e_pbc_base(filename,        exact_v, 1, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_pbc_base(filename,        exact_v, 1, 1) 
    self.assertEqual(check, 0)

  def test_pbc_na_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_pbc_na ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = -15073.7573775886
    check = td_fock1e_pbc_base(filename, exact_v, 1, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_pbc_base(filename, exact_v, 1, 1) 
    self.assertEqual(check, 0)

  def test_pbc_ecp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_pbc_ecp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = 165.112814886142
    check = td_fock1e_pbc_base(filename,        exact_v, 2, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_pbc_base(filename,        exact_v, 2, 1) 
    self.assertEqual(check, 0)

  def test_pbc_ecp_plus_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_pbc_ecp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v =  644.769597094371
    check = td_fock1e_pbc_base(filename, exact_v, 2, 0) 
    self.assertEqual(check, 0)
    check = td_fock1e_pbc_base(filename, exact_v, 2, 1) 
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



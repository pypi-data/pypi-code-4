

import unittest
import lotus_core_hpp
import math
import os

def td_grad_base(filename, exact_v, mode_u, sel_functor, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  ecps   = lotus_core_hpp.ECP.get_ecps_from_file(filename)
  if mode_mat==0:
    fock1e   = lotus_core_hpp.Fock1e()
    S        = lotus_core_hpp.dMatrix()
    X_a      = lotus_core_hpp.dMatrix()
    X_b      = lotus_core_hpp.dMatrix()
  elif mode_mat==1:
    fock1e   = lotus_core_hpp.Fock1e_map()
    S        = lotus_core_hpp.dMatrix_map()
    X_a      = lotus_core_hpp.dMatrix_map()
    X_b      = lotus_core_hpp.dMatrix_map()

  lamda   = lotus_core_hpp.get_vector_double()
  lamda_b = lotus_core_hpp.get_vector_double()
  scf     = lotus_core_hpp.SCF()
  grad    = lotus_core_hpp.Gradient()
  moldata = lotus_core_hpp.MolData()
  moldata.set_basis_from_file(filename)

  if sel_functor==0: functor = lotus_core_hpp.HF_Functor()
  if sel_functor==1: functor = lotus_core_hpp.Slater_Functor()
  if sel_functor==2: functor = lotus_core_hpp.B88_Functor()
  if sel_functor==3: functor = lotus_core_hpp.SVWN_Functor()
  if sel_functor==4: functor = lotus_core_hpp.BLYP_Functor()
  if sel_functor==5: functor = lotus_core_hpp.B3LYP_Functor()
 

  if mode_u==0:
    scf.guess_h_core(X_a, lamda, moldata.scgtos, moldata.ecps)
    eri = lotus_core_hpp.ERI_incore()
    scf.r_scf_debug(X_a, lamda, moldata, eri, functor) 

    occ    = lotus_core_hpp.Util.cal_occ(scgtos, ecps, 0, 1)
    force  = grad.cal_force(moldata.scgtos, moldata.ecps, X_a, occ, lamda, functor)
  if mode_u==1:
    scf.guess_h_core(X_a, lamda, moldata.scgtos, moldata.ecps)
    lotus_core_hpp.mat_copy(X_b, X_a) 
    eri = lotus_core_hpp.ERI_incore()
    scf.u_scf_debug(X_a, X_b, lamda, lamda_b, moldata, eri, functor) 

    occ_a = lotus_core_hpp.get_vector_double()
    occ_b = lotus_core_hpp.get_vector_double()
    lotus_core_hpp.Util.cal_occ_ab(occ_a, occ_b, moldata.scgtos, moldata.ecps, moldata.mol_charge, moldata.spin)
    force = grad.cal_force_u(moldata.scgtos, moldata.ecps, X_a, X_b, occ_a, occ_b, lamda, lamda_b, functor)
 
 
  check_v  = lotus_core_hpp.get_vector_double(3)
  check_v[0]=0.0
  check_v[1]=0.0
  check_v[2]=0.0
  for a in range( len(force)/3 ):
    check_v[0] += math.sqrt(force[a*3+0]*force[a*3+0]) 
    check_v[1] += math.sqrt(force[a*3+1]*force[a*3+1]) 
    check_v[2] += math.sqrt(force[a*3+2]*force[a*3+2]) 
    print "a=",a,"  force ",force[a*3+0],force[a*3+1],force[a*3+2],"check_v",check_v[0],check_v[1],check_v[2]

  ret=0
  process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
  abs_error=1.0e-7
  if abs( check_v[0]-exact_v[0])>abs_error or abs(check_v[1]-exact_v[1])>abs_error or \
     abs( check_v[2]-exact_v[2])>abs_error:
    ret=1
    if process_num==0:
      print " ----- in td_grad_base -----"
      print "   exact_v[0]",exact_v[0],"check_v[0]",check_v[0],"diff",exact_v[0]-check_v[0]
      print "   exact_v[1]",exact_v[1],"check_v[1]",check_v[1],"diff",exact_v[1]-check_v[1]
      print "   exact_v[2]",exact_v[2],"check_v[2]",check_v[2],"diff",exact_v[2]-check_v[2]

  return ret





class td_grad(unittest.TestCase):
  
  def setUp(self):
    pass

  def fun_grad_sub(self, filename, exact_v, sel_functor):
    check = td_grad_base(filename, exact_v, 0, sel_functor, 0) 
    self.assertEqual(check, 0)
    check = td_grad_base(filename, exact_v, 0, sel_functor, 1) 
    self.assertEqual(check, 0)
    check = td_grad_base(filename, exact_v, 1, sel_functor, 0) 
    self.assertEqual(check, 0)
    check = td_grad_base(filename, exact_v, 1, sel_functor, 1) 
    self.assertEqual(check, 0)
 
 
  def test_grad_hf(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_hf ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 0.3493498502009253,
                0.0000000000000000,
                0.4544301004312827]
    self.fun_grad_sub(filename, exact_v, 0)

  def test_grad_hf_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_hf_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 0.3427749363440474,
                0.0000000000000000,
                0.4309958979772428]
    self.fun_grad_sub(filename_d, exact_v, 0)

  def test_grad_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_svwn ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 2.405923838182816e-01,
                0.0000000000000000,
                2.895087230952800e-01]
    self.fun_grad_sub(filename, exact_v, 3)

  def test_grad_svwn_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_svwn_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 2.448015576864108e-01,
                0.0000000000000000,
                2.818207168152005e-01]
    self.fun_grad_sub(filename_d, exact_v, 3)

  def test_grad_blyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_blyp_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 2.220973708021526e-01,
                0.0000000000000000,
                2.539773201615168e-01]
    self.fun_grad_sub(filename_d, exact_v, 4)

  def test_grad_b3lyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_grad_b3lyp_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 2.516472744362920e-01,
                0.0000000000000000,
                2.974812046657984e-01]
    self.fun_grad_sub(filename_d, exact_v, 5)




def run_test():
  try:
    from mpi4py import MPI
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
  except:
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"

  if process_num==0: print " ##### test7.py #####"
  suite = unittest.TestLoader().loadTestsFromTestCase(td_grad)
  try:
    import xmlrunner
    testRunner = xmlrunner.XMLTestRunner()
  except:
    if process_num==0: print " unittest-xml-reporting is not installed"
    testRunner = unittest.TextTestRunner()

  unittest.TextTestRunner().run(suite)


if __name__ == "__main__":
  run_test()


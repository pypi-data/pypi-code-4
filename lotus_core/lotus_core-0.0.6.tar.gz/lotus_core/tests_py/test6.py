
import unittest
import lotus_core_hpp
import lotus_core
import math
import os



def td_scf_base(filename, exact_v, mode, sel_eri, sel_functor, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  ecps   = lotus_core_hpp.ECP.get_ecps_from_file(filename)

  if mode_mat==0:
    fock1e   = lotus_core_hpp.Fock1e()
    S        = lotus_core_hpp.dMatrix()
    D        = lotus_core_hpp.dMatrix()
    checkM_a = lotus_core_hpp.dMatrix()
    checkM_b = lotus_core_hpp.dMatrix()
  elif mode_mat==1:
    fock1e   = lotus_core_hpp.Fock1e_map()
    S        = lotus_core_hpp.dMatrix_map()
    D        = lotus_core_hpp.dMatrix_map()
    checkM_a = lotus_core_hpp.dMatrix_map()
    checkM_b = lotus_core_hpp.dMatrix_map()

  lamda   = lotus_core_hpp.get_vector_double()
  lamda_b = lotus_core_hpp.get_vector_double()
  scf     = lotus_core_hpp.SCF()

  if sel_eri==0: eri = lotus_core_hpp.ERI_direct() 
  if sel_eri==1: eri = lotus_core_hpp.ERI_file() 
  if sel_eri==2: eri = lotus_core_hpp.ERI_incore() 

  if sel_functor==0: functor = lotus_core_hpp.HF_Functor()
  if sel_functor==1: functor = lotus_core_hpp.Slater_Functor()
  if sel_functor==2: functor = lotus_core_hpp.B88_Functor()
  if sel_functor==3: functor = lotus_core_hpp.SVWN_Functor()
  if sel_functor==4: functor = lotus_core_hpp.BLYP_Functor()
  if sel_functor==5: functor = lotus_core_hpp.B3LYP_Functor()

  fock1e.cal_S(S, scgtos)

  process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
  if process_num==0: print "type(S)", type(S)
  abs_error=1.0e-9

  if mode==0:  # cal_h_core
    scf.cal_h_core(checkM_a, scgtos, ecps)
    check_a = lotus_core_hpp.Util.cal_DV(S, checkM_a)
    check_b = 0.0
  if mode==1:  # guess_h_core
    scf.guess_h_core(checkM_a, lamda, scgtos, ecps)
    occ = lotus_core_hpp.Util.cal_occ(scgtos, ecps, 0, 1)
    check_a = 0.0
    for i in range( len(lamda) ): check_a+=math.sqrt(lamda[i]*lamda[i])
    lotus_core_hpp.Util.cal_D(D, checkM_a, occ)
    check_b = lotus_core_hpp.Util.cal_DV(S, D)
  if mode==2: # cal_Fock_sub
    scf.prepare_eri(eri, scgtos) 
    scf.cal_Fock_sub(checkM_a, S, scgtos, eri, functor)
    check_a = lotus_core_hpp.Util.cal_DV(S, checkM_a)
    check_b = check_a
  if mode==3: # r_scf
    moldata = lotus_core_hpp.MolData()
    moldata.set_basis_from_file(filename)
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps)
    scf.r_scf_debug(checkM_a, lamda, moldata, eri, functor)
    abs_error=1.0e-5
    check_a = scf.get_ene_total()
    check_b = 0.0
    for i in range( len(lamda) ):  check_b += math.sqrt( lamda[i]*lamda[i] )
  if mode==4: # cal_Fock_sub_u
    scf.prepare_eri(eri, scgtos) 
    scf.cal_Fock_sub_u(checkM_a, checkM_b, S, S, scgtos, eri, functor)
    check_a = lotus_core_hpp.Util.cal_DV(S, checkM_a)
    check_b = lotus_core_hpp.Util.cal_DV(S, checkM_b)
  if mode==5: # u_scf
    moldata = lotus_core_hpp.MolData()
    moldata.set_basis_from_file(filename)
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps)
    lotus_core_hpp.mat_copy(checkM_b, checkM_a)
    scf.u_scf_debug(checkM_a, checkM_b, lamda, lamda_b, moldata, eri, functor)
    abs_error=1.0e-5
    check_a = scf.get_ene_total()
    check_b = 0.0
    for i in range( len(lamda) ):  check_b += math.sqrt( lamda[i]*lamda[i] )
  if mode==6: # r_rsc, eddis
    moldata = lotus_core_hpp.MolData()
    moldata.set_basis_from_file(filename)
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps)
    scf.do_ediis()
    scf.r_scf_debug(checkM_a, lamda, moldata, eri, functor)
    abs_error=1.0e-5
    check_a = scf.get_ene_total()
    check_b = 0.0
    for i in range( len(lamda) ):  check_b += math.sqrt( lamda[i]*lamda[i] )
    scf.do_diis()
  if mode==7: # u_rsc, eddis
    moldata = lotus_core_hpp.MolData()
    moldata.set_basis_from_file(filename)
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps)
    lotus_core_hpp.mat_copy(checkM_b, checkM_a)
    scf.do_ediis()
    scf.u_scf_debug(checkM_a, checkM_b, lamda, lamda_b, moldata, eri, functor)
    abs_error=1.0e-5
    check_a = scf.get_ene_total()
    check_b = 0.0
    for i in range( len(lamda) ):  check_b += math.sqrt( lamda[i]*lamda[i] )
    scf.do_diis()

 
  ret=0
  if math.fabs( check_a - exact_v[0])>abs_error or math.fabs( check_b - exact_v[1] )>abs_error:
    ret=1
    if process_num==0:
      print " ----- in td_dft_mat_pbc_base -----"
      print "   exact_v[0]",exact_v[0],"check_a",check_a,"diff",exact_v[0]-check_a
      print "   exact_v[1]",exact_v[1],"check_b",check_b,"diff",exact_v[1]-check_b

  return ret



class td_scf(unittest.TestCase):
  
  def setUp(self):
    pass

  def test_h_core(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_h_core ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -35.78070460897100,
                  0.00000000000000]
    check = td_scf_base(filename, exact_v, 0, 0, 0, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 0, 0, 0, 1)
    self.assertEqual(check, 0)


  def test_h_core_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_h_core_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -83.2612514756841,
                  0.00000000000000]
    check = td_scf_base(filename_d, exact_v, 0, 0, 0, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename_d, exact_v, 0, 0, 0, 1)
    self.assertEqual(check, 0)


  def test_guess_h_core(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_guess_h_core ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [  29.374285177441323,
                  4.00000000000000]
    check = td_scf_base(filename, exact_v, 1, 0, 0, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 1, 0, 0, 1)
    self.assertEqual(check, 0)

  def test_guess_h_core_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_guess_h_core_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [  43.520839858474474,
                  4.00000000000000]
    check = td_scf_base(filename_d, exact_v, 1, 0, 0, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename_d, exact_v, 1, 0, 0, 1)
    self.assertEqual(check, 0)

  def fun_fock_sub(self, filename, exact_v, sel_functor):
    check = td_scf_base(filename, exact_v, 2, 0, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 2, 1, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 2, 2, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 2, 0, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 2, 1, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 2, 2, sel_functor, 1)
    self.assertEqual(check, 0)

    check = td_scf_base(filename, exact_v, 4, 0, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 4, 1, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 4, 2, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 4, 0, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 4, 1, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 4, 2, sel_functor, 1)
    self.assertEqual(check, 0)

  
  def test_fock_sub_hf(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_hf ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 56.2569474715606,
                56.2569474715606]
    self.fun_fock_sub(filename, exact_v, 0)

  def test_fock_sub_hf_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_hf_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 358.004821713946512,
                358.004821713946512]
    self.fun_fock_sub(filename_d, exact_v, 0)

  def test_fock_sub_slater(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_slater ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 63.7215726251014,
                63.7215726251014]
    self.fun_fock_sub(filename, exact_v, 1)

  def test_fock_sub_slater_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_slater_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 421.3833226925,
                421.3833226925]
    self.fun_fock_sub(filename_d, exact_v, 1)

  def test_fock_sub_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_svwn ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 63.0684437711931,
                63.0684437711931]
    self.fun_fock_sub(filename, exact_v, 3)

  def test_fock_sub_svwn_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_svwn_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 419.581641410476,
                419.581641410476]
    self.fun_fock_sub(filename_d, exact_v, 3)

  def test_fock_sub_b3lyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_b3lyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 61.6831388827002,
                61.6831388827002]
    self.fun_fock_sub(filename, exact_v, 5)

  def test_fock_sub_b3lyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock_sub_b3lyp_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 407.335528628417,
                407.335528628417]
    self.fun_fock_sub(filename_d, exact_v, 5)

  def fun_scf_sub(self, filename, exact_v, sel_functor):
    check = td_scf_base(filename, exact_v, 3, 0, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 3, 1, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 3, 2, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 3, 0, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 3, 1, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 3, 2, sel_functor, 1)
    self.assertEqual(check, 0)
    
    check = td_scf_base(filename, exact_v, 5, 0, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 5, 1, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 5, 2, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 5, 0, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 5, 1, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 5, 2, sel_functor, 1)
    self.assertEqual(check, 0)

  def test_scf_hf(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_hf ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -15.997926929989090,
                  4.074002074868483]
    self.fun_scf_sub(filename, exact_v, 0)

  def test_scf_hf_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_hf_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -16.049785900583380,
                 23.509691116412167]
    self.fun_scf_sub(filename_d, exact_v, 0)

  def test_scf_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_svwn ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -16.31968247914776,
                  3.021254946143811]
    self.fun_scf_sub(filename, exact_v, 3)
  
  def test_scf_svwn_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_svwn_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -16.38449153649990,
                 19.61019670025221]
    self.fun_scf_sub(filename_d, exact_v, 3)

  def test_scf_b88(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_b88 ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -1.604226179160642e+01,
                 3.061640994030337e+00]
    self.fun_scf_sub(filename, exact_v, 2)

  def test_scf_b88_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_b88_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -1.609867110753819e+01,
                 1.999830828181901e+01]
    self.fun_scf_sub(filename_d, exact_v, 2)

  def test_scf_blyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_blyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -1.628869168612131e+01,
                 2.994283808452439e+00]
    self.fun_scf_sub(filename, exact_v, 4)
 
  def test_scf_blyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_blyp_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -1.634477586490963e+01,
                 1.972139477046332e+01]
    self.fun_scf_sub(filename_d, exact_v, 4)
 
  def test_scf_b3lyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_b3lyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -1.632746012006390e+01,
                 3.122207493754346e+00]
    self.fun_scf_sub(filename, exact_v, 5)

  def test_scf_b3lyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_b3lyp_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -1.638284192429592e+01,
                 2.028712129082399e+01]
    self.fun_scf_sub(filename_d, exact_v, 5)

  def fun_scf_sub_ediis(self, filename, exact_v, sel_functor):
    check = td_scf_base(filename, exact_v, 6, 0, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 6, 1, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 6, 2, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 6, 0, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 6, 1, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 6, 2, sel_functor, 1)
    self.assertEqual(check, 0)
    
    check = td_scf_base(filename, exact_v, 7, 0, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 7, 1, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 7, 2, sel_functor, 0)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 7, 0, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 7, 1, sel_functor, 1)
    self.assertEqual(check, 0)
    check = td_scf_base(filename, exact_v, 7, 2, sel_functor, 1)
    self.assertEqual(check, 0)

  def test_scf_hf_ediis(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_hf_ediis ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ -15.997926929989090,
                  4.074002074868483]
    self.fun_scf_sub_ediis(filename, exact_v, 0)

  def test_scf_hf_ediis_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_scf_hf_ediis_d ====="
    filename_d = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ -16.049785900583380,
                 23.509691116412167]
    self.fun_scf_sub_ediis(filename_d, exact_v, 0)


def run_test():
  try:
    from mpi4py import MPI
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
  except:
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"

  if process_num==0: print " ##### test6.py #####"
  suite = unittest.TestLoader().loadTestsFromTestCase(td_scf)
  try:
    import xmlrunner
    testRunner = xmlrunner.XMLTestRunner()
  except:
    if process_num==0: print " unittest-xml-reporting is not installed"
    testRunner = unittest.TextTestRunner()

  unittest.TextTestRunner().run(suite)


if __name__ == "__main__":
  run_test()


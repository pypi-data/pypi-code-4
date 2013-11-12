

import unittest
import lotus_core_hpp
import lotus_core
import math
import os


def td_lotus_base2(filename, exact_v, sel_functor, mode_mat):
   
  if mode_mat==0:
    lts     = lotus_core.create_lotus("dMatrix")
  if mode_mat==1:
    lts     = lotus_core.create_lotus("dMatrix_map")

  process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
  if process_num==0: print type(lts)

  if sel_functor==0: functor = lotus_core_hpp.HF_Functor()
  if sel_functor==1: functor = lotus_core_hpp.Slater_Functor()
  if sel_functor==2: functor = lotus_core_hpp.B88_Functor()
  if sel_functor==3: functor = lotus_core_hpp.SVWN_Functor()
  if sel_functor==4: functor = lotus_core_hpp.BLYP_Functor()
  if sel_functor==5: functor = lotus_core_hpp.B3LYP_Functor()

  lts.read_in_file(filename)
  lts.env_mol.functor=functor
  lts.guess_h_core()
  lts.scf_py()
  force = lts.cal_force_py()  
 
  check_v = lotus_core_hpp.get_vector_double(4)
  check_v[0] = lts.ene_total
  check_v[1]=0.0
  check_v[2]=0.0
  check_v[3]=0.0
  for a in range( len(force)/3 ):
    check_v[1] += math.sqrt(force[a*3+0]*force[a*3+0]) 
    check_v[2] += math.sqrt(force[a*3+1]*force[a*3+1]) 
    check_v[3] += math.sqrt(force[a*3+2]*force[a*3+2]) 

  ret=0
  abs_error=1.0e-6
  if abs( check_v[0]-exact_v[0])>abs_error or abs(check_v[1]-exact_v[1])>abs_error or \
     abs( check_v[2]-exact_v[2])>abs_error or abs(check_v[3]-exact_v[3])>abs_error:
    ret=1
    if process_num==0:
      print " ----- in td_lotus_base2 -----"
      print "   exact_v[0]",exact_v[0],"check_v[0]",check_v[0],"diff",exact_v[0]-check_v[0]
      print "   exact_v[1]",exact_v[1],"check_v[1]",check_v[1],"diff",exact_v[1]-check_v[1]
      print "   exact_v[2]",exact_v[2],"check_v[2]",check_v[2],"diff",exact_v[2]-check_v[2]
      print "   exact_v[3]",exact_v[3],"check_v[3]",check_v[3],"diff",exact_v[3]-check_v[3]

  return ret


class td_lotus2(unittest.TestCase):
  
  def setUp(self):
    pass

  def test_hcch_hf(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_hcch_hf ====="
    filename_hcch = os.path.abspath(os.path.dirname(__file__))+"/hcch.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -7.680140602139556e+01;
    exact_v[1] =  0.0;
    exact_v[2] =  0.0;
    exact_v[3] =  2.849170884926731e-01;
    check = td_lotus_base2(filename_hcch, exact_v, 0, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_hcch, exact_v, 0, 1)
    self.assertEqual(check, 0)
  
  def test_hcch_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_hcch_svwn ====="
    filename_hcch = os.path.abspath(os.path.dirname(__file__))+"/hcch.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -7.683983310700512e+01;
    exact_v[1] =  0.0;
    exact_v[2] =  0.0;
    exact_v[3] =  2.756369560779042e-01; 
    check = td_lotus_base2(filename_hcch, exact_v, 3, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_hcch, exact_v, 3, 1)
    self.assertEqual(check, 0)

  def test_hcch_b88(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_hcch_b88 ====="
    filename_hcch = os.path.abspath(os.path.dirname(__file__))+"/hcch.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -7.683293574418317e+01;
    exact_v[1] =  0.0;
    exact_v[2] =  0.0;
    exact_v[3] =  2.719936081708922e-01;
    check = td_lotus_base2(filename_hcch, exact_v, 2, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_hcch, exact_v, 2, 1)
    self.assertEqual(check, 0)
  
  def test_hcch_b3lyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_hcch_b3lyp ====="
    filename_hcch = os.path.abspath(os.path.dirname(__file__))+"/hcch.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -7.731144645033552e+01;
    exact_v[1] =  0.0;
    exact_v[2] =  0.0;
    exact_v[3] =  2.730583258161785e-01;
    check = td_lotus_base2(filename_hcch, exact_v, 5, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_hcch, exact_v, 5, 1)
    self.assertEqual(check, 0)

  def test_alanine_hf(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_alanine_hf ====="
    filename_alanine = os.path.abspath(os.path.dirname(__file__))+"/alanine.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -2.481285984093691e+02;
    exact_v[1] =  8.330032027968924e-02;
    exact_v[2] =  1.256274027153565e-01;
    exact_v[3] =  6.616315844422377e-02;
    check = td_lotus_base2(filename_alanine, exact_v, 0, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_alanine, exact_v, 0, 1)
    self.assertEqual(check, 0)

  def test_alanine_b3lyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_alanine_b3lyp ====="
    filename_alanine = os.path.abspath(os.path.dirname(__file__))+"/alanine.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -2.496889632812021e+02;
    exact_v[1] =  4.761406741095729e-02;
    exact_v[2] =  5.353982718038575e-02;
    exact_v[3] =  4.609678623533991e-02;
    check = td_lotus_base2(filename_alanine, exact_v, 5, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_alanine, exact_v, 5, 1)
    self.assertEqual(check, 0)

  def test_benzene_hf(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_benzene_hf ====="
    filename_benzene = os.path.abspath(os.path.dirname(__file__))+"/benzene.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -2.306870098715535e+02;
    exact_v[1] =  4.608961796313462e-01;
    exact_v[2] =  3.991697000901296e-01;
    exact_v[3] =  4.798649697481912e-14;
    check = td_lotus_base2(filename_benzene, exact_v, 0, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_benzene, exact_v, 0, 1)
    self.assertEqual(check, 0)

  def test_benzene_b3lyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_benzene_b3lyp ====="
    filename_benzene = os.path.abspath(os.path.dirname(__file__))+"/benzene.in"
    exact_v = lotus_core_hpp.get_vector_double(4)
    exact_v[0] = -2.322297719351925e+02;
    exact_v[1] =  4.628016024795332e-01;
    exact_v[2] =  4.008556467263605e-01;
    exact_v[3] =  0.0;
    check = td_lotus_base2(filename_benzene, exact_v, 5, 0)
    self.assertEqual(check, 0)
    check = td_lotus_base2(filename_benzene, exact_v, 5, 1)
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


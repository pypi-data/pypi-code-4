

import unittest
import lotus_core_hpp
import math
import os


def td_dft_mat_base(filename, exact_v, mode_u, mode, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  if mode_mat==0:
    fock1e = lotus_core_hpp.Fock1e()
    ginteg = lotus_core_hpp.Grid_Inte()
    S      = lotus_core_hpp.dMatrix()
    Vxc_a  = lotus_core_hpp.dMatrix()
    Vxc_b  = lotus_core_hpp.dMatrix()
  elif mode_mat==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    ginteg = lotus_core_hpp.Grid_Inte_map()
    S      = lotus_core_hpp.dMatrix_map()
    Vxc_a  = lotus_core_hpp.dMatrix_map()
    Vxc_b  = lotus_core_hpp.dMatrix_map()

  fock1e.cal_S(S, scgtos)
  if mode==0:  functor = lotus_core_hpp.Slater_Functor()
  if mode==1:  functor = lotus_core_hpp.B88_Functor()
  if mode==2:  functor = lotus_core_hpp.SVWN_Functor()
  if mode==3:  functor = lotus_core_hpp.BLYP_Functor()
  if mode==4:  functor = lotus_core_hpp.B3LYP_Functor()

  if mode_u==0:  ene_dft = ginteg.grid_integral_mat(Vxc_a, S, scgtos, functor)
  else:          ene_dft = ginteg.grid_integral_mat_u(Vxc_a, Vxc_b, S, S, scgtos, functor)

  if mode_u==0:
    svxc_a = lotus_core_hpp.Util.cal_DV(S, Vxc_a)
    svxc_b = svxc_a
  else:
    svxc_a = lotus_core_hpp.Util.cal_DV(S, Vxc_a)
    svxc_b = lotus_core_hpp.Util.cal_DV(S, Vxc_b)
   
  ret=0
  if math.fabs( ene_dft - exact_v[0] )>1.0e-8 or \
     math.fabs( svxc_a  - exact_v[1] )>1.0e-8 or \
     math.fabs( svxc_b  - exact_v[2] )>1.0e-8:
    ret=1
    print " ----- error in td_dft_mat_base ----"
    print "   exact_v[0]",exact_v[0]," ene_dft  ",ene_dft," diff ",exact_v[0]-ene_dft
    print "   exact_v[1]",exact_v[1]," svsc_a   ",svxc_a, " diff ",exact_v[1]-svxc_a
    print "   exact_v[2]",exact_v[2]," svsc_a   ",svxc_b, " diff ",exact_v[2]-svxc_b

  return ret

  

def td_dft_grad_base(filename, exact_v, mode_u, mode, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  if mode_mat==0:
    fock1e = lotus_core_hpp.Fock1e()
    ginteg = lotus_core_hpp.Grid_Inte()
    S      = lotus_core_hpp.dMatrix()
  elif mode_mat==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    ginteg = lotus_core_hpp.Grid_Inte_map()
    S      = lotus_core_hpp.dMatrix_map()

  fock1e.cal_S(S, scgtos)
  if mode==0:  functor = lotus_core_hpp.Slater_Functor()
  if mode==1:  functor = lotus_core_hpp.B88_Functor()
  if mode==2:  functor = lotus_core_hpp.SVWN_Functor()
  if mode==3:  functor = lotus_core_hpp.BLYP_Functor()
  if mode==4:  functor = lotus_core_hpp.B3LYP_Functor()

  if mode_u==0:  grad = ginteg.cal_grad(scgtos, S, functor)
  else:          grad = ginteg.cal_grad_u(scgtos, S, S, functor)

  check_v = lotus_core_hpp.get_vector_double(3)
  for i in range(3): check_v[i]=0.0

  for a in range( len(grad)/3 ):
    check_v[0] += math.sqrt( grad[a*3+0]*grad[a*3+0] )
    check_v[1] += math.sqrt( grad[a*3+1]*grad[a*3+1] )
    check_v[2] += math.sqrt( grad[a*3+2]*grad[a*3+2] )

  ret=0
  if math.fabs( check_v[0] - exact_v[0])>1.0e-12 or \
     math.fabs( check_v[1] - exact_v[1])>1.0e-12 or \
     math.fabs( check_v[2] - exact_v[2])>1.0e-12:
    ret=1
    print " ----- in td_dft_grad_base -----"
    print "   exact_v[0]",exact_v[0],"check_v[0]",check_v[0],"diff",exact_v[0]-check_v[0]
    print "   exact_v[1]",exact_v[1],"check_v[1]",check_v[1],"diff",exact_v[1]-check_v[1]
    print "   exact_v[2]",exact_v[2],"check_v[2]",check_v[2],"diff",exact_v[2]-check_v[2]

  return ret

   

class td_dft(unittest.TestCase):
  
  def setUp(self):
    pass

  def fun_check(self, filename, exact_v, sel):
    check = td_dft_mat_base(filename, exact_v, 0, sel, 0)
    self.assertEqual(check, 0)
    check = td_dft_mat_base(filename, exact_v, 0, sel, 1)
    self.assertEqual(check, 0)
    check = td_dft_mat_base(filename, exact_v, 1, sel, 0)
    self.assertEqual(check, 0)
    check = td_dft_mat_base(filename, exact_v, 1, sel, 1)
    self.assertEqual(check, 0)


  # slater
  def test_dft_mat_slater(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_slater ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [-8.68918462925892,
               -5.79278975283834,
               -5.79278975283834]
    self.fun_check(filename, exact_v, 0)

  def test_dft_mat_slater_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_slater_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [-28.7225990726249,
               -19.1483993817468,
               -19.1483993817468]
    self.fun_check(filename, exact_v, 0)

  # b88
  def test_dft_mat_b88(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_b88 ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [-9.2876235408606,
               -6.03693727770248,
               -6.03693727770248]
    self.fun_check(filename, exact_v, 1)

  def test_dft_mat_b88_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_b88_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [-29.8278342726607,
               -19.5962495878738,
               -19.5962495878738]
    self.fun_check(filename, exact_v, 1)

  # svwn
  def test_dft_mat_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_svwn ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [-9.87546262859488,
               -6.4459186067467,
               -6.4459186067467]
    self.fun_check(filename, exact_v, 2)

  def test_dft_mat_svwn_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_svwn_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [-32.0105268520034,
               -20.9500806637708,
               -20.9500806637708]
    self.fun_check(filename, exact_v, 2)

  # blyp
  def test_dft_mat_blyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_blyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [-9.77158715290214,
               -6.34018173640426,
               -6.34018173640426]
    self.fun_check(filename, exact_v, 3)

  def test_dft_mat_blyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_blyp_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [-31.3144744951157,
               -20.4694869661171,
               -20.4694869661171]
    self.fun_check(filename, exact_v, 3)

  # b3lyp
  def test_dft_mat_b3lyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_b3lyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [-7.99962706538783,
               -5.17974051396373,
               -5.17974051396373]
    self.fun_check(filename, exact_v, 4)

  def test_dft_mat_b3lyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_mat_b3lyp_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [-25.6027334603965,
               -16.69081337377,
               -16.69081337377]
    self.fun_check(filename, exact_v, 4)

  #
  # gradient
  #
             
  def fun_grad_check(self, filename, exact_v, sel):
    check = td_dft_grad_base(filename, exact_v, 0, sel, 0)
    self.assertEqual(check, 0)
    check = td_dft_grad_base(filename, exact_v, 0, sel, 1)
    self.assertEqual(check, 0)
    check = td_dft_grad_base(filename, exact_v, 1, sel, 0)
    self.assertEqual(check, 0)
    check = td_dft_grad_base(filename, exact_v, 1, sel, 1)
    self.assertEqual(check, 0)

 
  # slater
  def test_dft_grad_slater(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_slater ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 1.05296460949943,
                0.00000000000000,
                1.55725111110006]
    self.fun_grad_check(filename, exact_v, 0)

  def test_dft_grad_slater_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_slater_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 2.87484447384673,
                0.00000000000000,
                4.16771240491097]
    self.fun_grad_check(filename, exact_v, 0)

  # b88
  def test_dft_grad_b88(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_b88 ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 1.04847620377321,
                0.00000000000000,
                1.56017486613892]
    self.fun_grad_check(filename, exact_v, 1)

  def test_dft_grad_b88_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_b88_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 2.91520808450086,
                0.00000000000000,
                4.22884556905654]
    self.fun_grad_check(filename, exact_v, 1)

  # svwn
  def test_dft_grad_svwn(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_svwn ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 1.14533141423903,
                0.00000000000000,
                1.69443739285219]
    self.fun_grad_check(filename, exact_v, 2)

  def test_dft_grad_svwn_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_svwn_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 3.08784188862778,
                0.00000000000000,
                4.4766019037608]
    self.fun_grad_check(filename, exact_v, 2)

  # blyp
  def test_dft_grad_blyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_blyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 1.10246933713149,
                0.00000000000000,
                1.63759463570879]
    self.fun_grad_check(filename, exact_v, 3)

  def test_dft_grad_blyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_blyp_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 3.02653535330202,
                0.00000000000000,
                4.38957440364052]
    self.fun_grad_check(filename, exact_v, 3)

  # b3lyp
  def test_dft_grad_b3lyp(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_b3lyp ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 0.900424166397432,
                0.000000000000000,
                 1.3366813993925]
    self.fun_grad_check(filename, exact_v, 4)

  def test_dft_grad_b3lyp_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_dft_grad_b3lyp_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 2.45958197528588,
                0.00000000000000,
                3.56706516290775]
    self.fun_grad_check(filename, exact_v, 4)

if __name__ == "__main__":
  try:
    from mpi4py import MPI
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
  except:
    lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"

  unittest.main(exit=False)


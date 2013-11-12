
import unittest
import lotus_core_hpp
import math
import os

def td_fock2e_Vh_and_Vx_base(filename, exact_v, mode_u, mode, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  if mode_mat==0:
    fock1e = lotus_core_hpp.Fock1e()
    fock2e = lotus_core_hpp.Fock2e()
    S      = lotus_core_hpp.dMatrix()
    Vh     = lotus_core_hpp.dMatrix()
    Vx_a   = lotus_core_hpp.dMatrix()
    Vx_b   = lotus_core_hpp.dMatrix()
  elif mode_mat==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    fock2e = lotus_core_hpp.Fock2e_map()
    S      = lotus_core_hpp.dMatrix_map()
    Vh     = lotus_core_hpp.dMatrix_map()
    Vx_a   = lotus_core_hpp.dMatrix_map()
    Vx_b   = lotus_core_hpp.dMatrix_map()

  fock1e.cal_S(S, scgtos)
  if mode==0:  sel_eri = lotus_core_hpp.ERI_direct()
  if mode==1:  sel_eri = lotus_core_hpp.ERI_file()
  if mode==2:  sel_eri = lotus_core_hpp.ERI_incore()

  fock2e.prepare_eri(sel_eri, scgtos)

  if mode_u==0: fock2e.cal_Vh_and_Vx(Vh, Vx_a, S, scgtos, sel_eri)
  else:         fock2e.cal_Vh_and_Vx_u(Vh, Vx_a, Vx_b, S, S, scgtos, sel_eri)
  
  svh   = lotus_core_hpp.Util.cal_DV(S, Vh)
  svx_a = lotus_core_hpp.Util.cal_DV(S, Vx_a)
  if mode_u==0: svx_b=svx_a
  else:         svx_b=lotus_core_hpp.Util.cal_DV(S, Vx_b)

  ret=0
  if math.fabs(svh   - exact_v[0])>1.0e-12 or \
     math.fabs(svx_a - exact_v[1])>1.0e-12 or \
     math.fabs(svx_b - exact_v[2])>1.0e-12:
    ret=1
    print " ----- error in td_fock2e_Vh_and Vx ----"
    print "   exact_v[0]",exact_v[0]," svh  ",svh,  " diff ",exact_v[0]-svh
    print "   exact_v[1]",exact_v[1]," svh  ",svx_a," diff ",exact_v[1]-svx_a
    print "   exact_v[2]",exact_v[2]," svh  ",svx_b," diff ",exact_v[2]-svx_b

  return ret


def td_fock2e_grad_base(filename, exact_v_h, exact_v_x, mode_u, mode_mat):
  scgtos = lotus_core_hpp.Util_GTO.get_scgtos_from_file(filename)
  if mode_mat==0:
    fock1e = lotus_core_hpp.Fock1e()
    fock2e = lotus_core_hpp.Fock2e()
    S      = lotus_core_hpp.dMatrix()
    Vh     = lotus_core_hpp.dMatrix()
    Vx_a   = lotus_core_hpp.dMatrix()
    Vx_b   = lotus_core_hpp.dMatrix()
  elif mode_mat==1:
    fock1e = lotus_core_hpp.Fock1e_map()
    fock2e = lotus_core_hpp.Fock2e_map()
    S      = lotus_core_hpp.dMatrix_map()
    Vh     = lotus_core_hpp.dMatrix_map()
    Vx_a   = lotus_core_hpp.dMatrix_map()
    Vx_b   = lotus_core_hpp.dMatrix_map()

  fock1e.cal_S(S, scgtos)
  grad_h = lotus_core_hpp.get_vector_double(1)
  grad_x = lotus_core_hpp.get_vector_double(1)
  if mode_u==0: fock2e.cal_grad(grad_h, grad_x, scgtos, S) 
  if mode_u==1: fock2e.cal_grad_u(grad_h, grad_x, scgtos, S, S) 

  check_v_h = lotus_core_hpp.get_vector_double(3)
  check_v_x = lotus_core_hpp.get_vector_double(3)
  for i in range(3):
    check_v_h[i]=0.0
    check_v_x[i]=0.0

  for a in range( len(grad_h)/3 ):
    check_v_h[0] += math.sqrt( grad_h[a*3+0]*grad_h[a*3+0] )
    check_v_h[1] += math.sqrt( grad_h[a*3+1]*grad_h[a*3+1] )
    check_v_h[2] += math.sqrt( grad_h[a*3+2]*grad_h[a*3+2] )
    check_v_x[0] += math.sqrt( grad_x[a*3+0]*grad_x[a*3+0] )
    check_v_x[1] += math.sqrt( grad_x[a*3+1]*grad_x[a*3+1] )
    check_v_x[2] += math.sqrt( grad_x[a*3+2]*grad_x[a*3+2] )

  ret=0
  if math.fabs( check_v_h[0] - exact_v_h[0])>1.0e-13 or \
     math.fabs( check_v_h[1] - exact_v_h[1])>1.0e-13 or \
     math.fabs( check_v_h[2] - exact_v_h[2])>1.0e-13 or \
     math.fabs( check_v_x[0] - exact_v_x[0])>1.0e-13 or \
     math.fabs( check_v_x[1] - exact_v_x[1])>1.0e-13 or \
     math.fabs( check_v_x[2] - exact_v_x[2])>1.0e-13:
    print " ----- in td_fock2e_grad_base -----"
    print "   exact_v_h[0]",exact_v_h[0],"check_v_h[0]",check_v_h[0],"diff",exact_v_h[0]-check_v_h[0]
    print "   exact_v_h[1]",exact_v_h[1],"check_v_h[1]",check_v_h[1],"diff",exact_v_h[1]-check_v_h[1]
    print "   exact_v_h[2]",exact_v_h[2],"check_v_h[2]",check_v_h[2],"diff",exact_v_h[2]-check_v_h[2]
    print "   exact_v_x[0]",exact_v_x[0],"check_v_x[0]",check_v_x[0],"diff",exact_v_x[0]-check_v_x[0]
    print "   exact_v_x[1]",exact_v_x[1],"check_v_x[1]",check_v_x[1],"diff",exact_v_x[1]-check_v_x[1]
    print "   exact_v_x[2]",exact_v_x[2],"check_v_x[2]",check_v_x[2],"diff",exact_v_x[2]-check_v_x[2]

  return ret

class td_fock2e(unittest.TestCase):
  
  def setUp(self):
    pass

  def test_Vh_and_Vx(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_Vh_and_Vx ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 69.514362377939790,
               -13.257414906379237,
               -13.257414906379237]
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 0, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 0, 1)
    self.assertEqual(check, 0)

    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 1, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 1, 1)
    self.assertEqual(check, 0)

    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 2, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 2, 1)
    self.assertEqual(check, 0)

  def test_Vh_and_Vx_u(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_Vh_and_Vx_u ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v = [ 69.514362377939790,
               -13.257414906379237,
               -13.257414906379237]
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 0, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 0, 1)
    self.assertEqual(check, 0)
  
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 1, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 1, 1)
    self.assertEqual(check, 0)

    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 2, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 2, 1)
    self.assertEqual(check, 0)
  
  def test_Vh_and_Vx_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_Vh_and_Vx_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 440.531722074247114,
                -82.526900360300203,
                -82.526900360300203]
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 0, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 0, 1)
    self.assertEqual(check, 0)
  
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 1, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 1, 1)
    self.assertEqual(check, 0)
  
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 2, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 0, 2, 1)
    self.assertEqual(check, 0)
  
  def test_Vh_and_Vx_du(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_Vh_and_Vx_du ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v = [ 440.531722074247114,
                -82.526900360300203,
                -82.526900360300203]
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 0, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 0, 1)
    self.assertEqual(check, 0)
  
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 1, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 1, 1)
    self.assertEqual(check, 0)
 
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 2, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_Vh_and_Vx_base(filename, exact_v, 1, 2, 1)
    self.assertEqual(check, 0)
 
  def test_fock2e_grad(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock2e_grad ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v_h = [13.5690070385031,
                  0.0000000000000,
                 18.791046595282]
    exact_v_x = [ 3.37495707732413,
                  0.00000000000000,
                  4.90195505988168]
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 0, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 0, 1)
    self.assertEqual(check, 0)
 
  def test_fock2e_grad_u(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock2e_grad_u ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc.mol"
    exact_v_h = [13.5690070385031,
                  0.0000000000000,
                 18.791046595282]
    exact_v_x = [ 3.37495707732413,
                  0.00000000000000,
                  4.90195505988168]
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 1, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 1, 1)
    self.assertEqual(check, 0)
            
  def test_fock2e_grad_d(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock2e_grad_d ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v_h = [61.2241334993477,
                  0.0000000000000,
                 86.6223405609601]
    exact_v_x = [16.1830503526459,
                  0.0000000000000,
                 23.2646314515965]
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 0, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 0, 1)
    self.assertEqual(check, 0)
            
  def test_fock2e_grad_du(self):
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print "\n===== test_fock2e_grad_du ====="
    filename = os.path.abspath(os.path.dirname(__file__))+"/h2o_sbkjc_plus_d.mol"
    exact_v_h = [61.2241334993477,
                  0.0000000000000,
                 86.6223405609601]
    exact_v_x = [16.1830503526459,
                  0.0000000000000,
                 23.2646314515965]
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 1, 0)
    self.assertEqual(check, 0)
    check = td_fock2e_grad_base(filename, exact_v_h, exact_v_x, 1, 1)
    self.assertEqual(check, 0)
 
              

if __name__ == "__main__":
  try:
    from mpi4py import MPI
  except:
    process_num = lotus_core_hpp.Util_MPI.get_mpi_rank()
    if process_num==0: print " mpi4py is not installed"
  lotus_core_hpp.Util_MPI.set_MPI_COMM_LOTUS()

  unittest.main()



import unittest
import test1
import test2
import test3
import test4
import test5
import test6
import test7
import test8
import test9


def suite(): 
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(test1.td_fock1e))
  suite.addTests(unittest.makeSuite(test2.td_fock2e))
  suite.addTests(unittest.makeSuite(test3.td_dft))
  suite.addTests(unittest.makeSuite(test4.td_dft_pbc))
  suite.addTests(unittest.makeSuite(test5.td_matrix))
  suite.addTests(unittest.makeSuite(test6.td_scf))
  suite.addTests(unittest.makeSuite(test7.td_grad))
  suite.addTests(unittest.makeSuite(test8.td_lotus))
  suite.addTests(unittest.makeSuite(test9.td_lotus2))
  return suite



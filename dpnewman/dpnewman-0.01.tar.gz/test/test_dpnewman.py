# -*- coding: utf-8 -*-
import numpy as np
import dpnewman
import unittest

class DPNewmanTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def testdpnewman(self):
        mat = np.array([[0,1,1,1,0,0,0,0,0],
                        [1,0,1,1,0,0,0,0,0],
                        [1,1,0,1,0,0,0,0,0],
                        [1,1,1,0,0,0,1,0,0],
                        [0,0,0,0,0,1,1,1,1],
                        [0,0,0,0,1,0,1,1,1],
                        [0,0,0,0,1,1,0,1,1],
                        [0,0,0,0,1,1,1,0,1],
                        [0,0,0,0,1,1,1,1,0]])
        mat=mat.astype(np.float64)
        g = dpnewman.DPNewman(T=100,c1=10.0,c2=1.0,phi=0.5,thresh=0.1)
        g.fit(mat)
        print g.get_cluster()

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(DPNewmanTestCase))
    return suite


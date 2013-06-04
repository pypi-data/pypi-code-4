#!/usr/bin/env python

import os
import sys
import copy
import unittest

from satispy import *
from satispy.io import *
from satispy.solver import *

class VariableTest(unittest.TestCase):
    def testVariable(self):
        v = Variable("name")
        self.assertEqual("name", str(v))
        self.assertEqual("-name", str(-v))

    def testName(self):
        v1 = Variable('v1')
        self.assertEqual('v1', v1.name)

    def testInverted(self):
        v1 = Variable('v1')
        v2 = Variable('v2', 1)

        self.assertEqual(0, v1.inverted)
        self.assertEqual(1, v2.inverted)
        self.assertRaises(ValueError, Variable, 'v3', 2)

    def testNegation(self):
        v1 = Variable('v1')
        v2 = Variable('v2', 1)

        self.assertEqual(1, (-v1).inverted)
        self.assertEqual(0, (-v2).inverted)

class CnfTest(unittest.TestCase):
    def testInit(self):
        cnf = Cnf()
        self.assertEqual("", cnf.getBuffer())

    #~ def testAnd(self):
        #~ v1 = Variable("v1")
        #~ v2 = Variable("v2")
        #~ cnf = v1 & v2
        #~ self.assertEqual(set([frozenset([v1]),frozenset([v2])]), set(cnf.dis))

    def testOr(self):
        v1 = Variable("v1")
        v2 = Variable("v2")

        cnf = v1 | v2

        val = 1 << v1.number | 1 << v2.number

        self.assertEqual(val, reduce(lambda x, y: 256*x+ord(y), cnf.getBuffer(), 0))
#~ 
        #~ cnf2 = cnf1 | v3
#~ 
        #~ self.assertEqual(set([frozenset([v1,v2,v3])]), set(cnf2.dis))
#~ 
        #~ # Test empty CNF or
        #~ cnf = Cnf()
        #~ cnf |= v1
#~ 
        #~ self.assertEqual(set([frozenset([v1])]), set(cnf.dis))
#~ 
    #~ def testCreateFrom(self):
        #~ v1 = Variable("v1")
        #~ self.assertEqual(set([frozenset([v1])]), set(Cnf.create_from(v1).dis))
#~ 
    #~ def testMixed(self):
        #~ v1 = Variable("v1")
        #~ v2 = Variable("v2")
        #~ v3 = Variable("v3")
        #~ v4 = Variable("v4")
#~ 
        #~ self.assertEqual(
            #~ set([
                #~ frozenset([v1,v2]),
                #~ frozenset([v3])
            #~ ]),
            #~ set(((v1 | v2) & v3).dis)
        #~ )
#~ 
        #~ # Distribution
        #~ self.assertEqual(
            #~ set([
                #~ frozenset([v1,v3]),
                #~ frozenset([v2,v3])
            #~ ]),
            #~ set(((v1 & v2) | v3).dis)
        #~ )
#~ 
        #~ # Double distribution
        #~ self.assertEqual(
            #~ set([
                #~ frozenset([v1,v3]),
                #~ frozenset([v1,v4]),
                #~ frozenset([v2,v3]),
                #~ frozenset([v2,v4])
            #~ ]),
            #~ set(((v1 & v2) | (v3 & v4)).dis)
        #~ )
#~ 
    #~ def testNegation(self):
        #~ v1 = Variable("v1")
        #~ v2 = Variable("v2")
        #~ v3 = Variable("v3")
#~ 
        #~ self.assertEqual(
            #~ set([frozenset([-v1])]),
            #~ set((-Cnf.create_from(v1)).dis)
        #~ )
#~ 
    #~ def testXor(self):
        #~ v1 = Variable("v1")
        #~ v2 = Variable("v2")
#~ 
        #~ cnf = v1 ^ v2
#~ 
        #~ self.assertEqual(
            #~ set([
                #~ frozenset([v1,v2]),
                #~ frozenset([-v1,-v2])
            #~ ]),
            #~ set(cnf.dis)
        #~ )
#~ 
    #~ def testImplication(self):
        #~ v1 = Variable("v1")
        #~ v2 = Variable("v2")
#~ 
        #~ self.assertEqual(
            #~ set([frozenset([-v1,v2])]),
            #~ set((v1 >> v2).dis)
        #~ )
#~ 
#~ class DimacsTest(unittest.TestCase):
    #~ def testDimacs(self):
        #~ v1 = Variable("v1")
        #~ v2 = Variable("v2")
        #~ v3 = Variable("v3")
        #~ v4 = Variable("v4")
#~ 
        #~ cnf1 = (v1 | v2) & (-v3 | v4) & (-v1 | v3 | -v4)
#~ 
        #~ io = DimacsCnf()
#~ 
        #~ s = io.tostring(cnf1)
#~ 
        #~ # Must be true because of Variable ordering, and
        #~ # the guarantee of numbering during IO
        #~ self.assertEqual(io.varname(v1), '1')
        #~ self.assertEqual(io.varname(v2), '2')
        #~ self.assertEqual(io.varname(v3), '3')
        #~ self.assertEqual(io.varname(v4), '4')
        #~ self.assertEqual(io.varobj('1'), v1)
        #~ self.assertEqual(io.varobj('2'), v2)
        #~ self.assertEqual(io.varobj('3'), v3)
        #~ self.assertEqual(io.varobj('4'), v4)
#~ 
        #~ cnf2 = io.fromstring(s)
#~ 
        #~ # Must be true due to io conventions
        #~ self.assertEqual(io.varname(v1), '1')
        #~ self.assertEqual(io.varname(v2), '2')
        #~ self.assertEqual(io.varname(v3), '3')
        #~ self.assertEqual(io.varname(v4), '4')
        #~ self.assertEqual(io.varobj('1'), v1)
        #~ self.assertEqual(io.varobj('2'), v2)
        #~ self.assertEqual(io.varobj('3'), v3)
        #~ self.assertEqual(io.varobj('4'), v4)
#~ 
        #~ # The frozenset is deterministic, so this will be ture
        #~ # if everything else is OK
        #~ self.assertEqual(cnf1, cnf2)
#~ 
#~ class MinisatTest(unittest.TestCase):
#~ 
    #~ def testSolution(self):
        #~ v1 = Variable("v1")
        #~ v2 = Variable("v2")
        #~ v3 = Variable("v3")
        #~ v4 = Variable("v4")
#~ 
        #~ cnf = (v1 | v2) & (-v3 | v4) & (-v1 | v3 | -v4)
        #~ #  v1, -v2, -v3, -v4
        #~ #  v1, -v2,  v3,  v4
        #~ #  v1,  v2, -v3, -v4
        #~ #  v1,  v2,  v3,  v4
        #~ # -v1,  v2, -v3, -v4
        #~ # -v1,  v2, -v3,  v4
        #~ # -v1,  v2,  v3,  v4
#~ 
        #~ solver = Minisat()
#~ 
        #~ sol = solver.solve(cnf)
#~ 
        #~ self.assertTrue(
            #~ (sol[v1],sol[v2], sol[v3], sol[v4])
            #~ in
            #~ [
                #~ (True,  False, False, False),
                #~ (True,  False, True,  True ),
                #~ (True,  True,  False, False),
                #~ (True,  True,  True,  True ),
                #~ (False, True,  False, False),
                #~ (False, True,  False, True ),
                #~ (False, True,  True,  True )
            #~ ]
        #~ )


if __name__ == "__main__":
    unittest.main()

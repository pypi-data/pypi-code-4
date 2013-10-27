#
# Unit Tests for Elements of a Model
#
# Test             Class to test the Model class
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo.base import IntegerSet
from coopr.pyomo import *
from coopr.opt import *
from coopr.pyomo.base.var import _VarElement
import pyutilib.th as unittest
import pyutilib.services

class Test(unittest.TestCase):

    def tearDown(self):
        if os.path.exists("unknown.lp"):
            os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_clear_attribute(self):
        """ Coverage of the _clear_attribute method """
        model = ConcreteModel()
        obj = Set()
        model.A = obj
        self.assertEqual(model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, model.A)

        obj = Var()
        model.A = obj
        self.assertEqual(model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, model.A)

        obj = Param()
        model.A = obj
        self.assertEqual(model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, model.A)

        obj = Objective()
        model.A = obj
        self.assertEqual(model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, model.A)

        obj = Constraint()
        model.A = obj
        self.assertEqual(model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, model.A)

        obj = Set()
        model.A = obj
        self.assertEqual(model.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, model.A)

    def test_set_attr(self):
        model = ConcreteModel()
        model.x = Param(mutable=True)
        model.x = 5
        self.assertEqual(value(model.x), 5)
        model.x = 6
        self.assertEqual(value(model.x), 6)
        try:
            model.x = None
            self.fail("Expected exception assigning None to domain Any")
        except ValueError:
            pass

    def test_write(self):
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        model.obj = Objective(rule=obj_rule)
        instance = model.create()
        instance.write()

    def test_write2(self):
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            return (1, model.x[1]+model.x[2], 2)
        model.c = Constraint(rule=c_rule)
        instance = model.create()
        instance.write()

    def test_write3(self):
        """Test that the summation works correctly, even though param 'w' has a default value"""
        model = ConcreteModel()
        model.J = RangeSet(1,4)
        model.w=Param(model.J, default=4)
        model.x=Var(model.J)
        def obj_rule(instance):
            return summation(instance.w, instance.x)
        model.obj = Objective(rule=obj_rule)
        instance = model.create()
        self.assertEqual(len(instance.obj[None].expr._args), 4)

    @unittest.skipIf(not pyutilib.services.registered_executable("glpsol"), "glpsol executable is not available")
    def test_solve1(self):
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        model.c = Constraint(rule=c_rule)
        instance = model.create()
        #instance.pprint()
        opt = SolverFactory('glpk')
        results = opt.solve(instance, keepfiles=True, symbolic_solver_labels=True)
        results.write(filename=currdir+"solve1.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1.out",currdir+"solve1.txt", tolerance=1e-4)
        #
        def d_rule(model):
            return model.x[1] >= 0
        model.d = Constraint(rule=d_rule)
        model.d.deactivate()
        instance = model.create()
        results = opt.solve(instance, keepfiles=True)
        results.write(filename=currdir+"solve1x.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1x.out",currdir+"solve1.txt", tolerance=1e-4)
        #
        model.d.activate()
        instance = model.create()
        results = opt.solve(instance, keepfiles=True)
        results.write(filename=currdir+"solve1a.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1a.out",currdir+"solve1a.txt", tolerance=1e-4)
        #
        model.d.deactivate()
        def e_rule(model, i):
            return model.x[i] >= 0
        model.e = Constraint(model.A, rule=e_rule)
        instance = model.create()
        for i in instance.A:
            instance.e[i].deactivate()
        results = opt.solve(instance, keepfiles=True)
        results.write(filename=currdir+"solve1b.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve1b.out",currdir+"solve1b.txt", tolerance=1e-4)

    def Xtest_load1(self):
        """Testing loading of vector solutions"""
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        model.c = Constraint(rule=c_rule)
        instance = model.create()
        ans = [0.75]*4
        instance.load(ans)
        instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1c.txt")

    
    @unittest.skipIf(not pyutilib.services.registered_executable("glpsol"), "glpsol executable is not available")
    def Xtest_solve2(self):
        """
        WEH - this is disabled because glpk appears to work fine
        on this example.  I'm not quite sure what has changed that has
        impacted this test...
        """
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        model.obj = Objective(rule=obj_rule)
        instance = model.create()
        #instance.pprint()
        opt = solvers.GLPK(keepfiles=True)
        solutions = opt.solve(instance)
        solutions.write()
        sys.exit(1)
        try:
            instance.load(solutions)
            self.fail("Cannot load a solution with a bad solver status")
        except ValueError:
            pass

    def test_solve3(self):
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        model.obj = Objective(rule=obj_rule)
        instance = model.create()
        instance.display(currdir+"solve3.out")
        self.assertFileEqualsBaseline(currdir+"solve3.out",currdir+"solve3.txt")

    @unittest.skipIf(not pyutilib.services.registered_executable("glpsol"), "glpsol executable is not available")
    def test_solve4(self):
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        model.c = Constraint(rule=c_rule)
        instance = model.create()
        #instance.pprint()
        opt = SolverFactory('glpk', keepfiles=True)
        results = opt.solve(instance, symbolic_solver_labels=True)
        results.write(filename=currdir+'solve4.out', format='json')
        self.assertMatchesJsonBaseline(currdir+"solve4.out",currdir+"solve1.txt", tolerance=1e-4)

    @unittest.skipIf(not pyutilib.services.registered_executable("glpsol"), "glpsol executable is not available")
    def Xtest_solve5(self):
        """ A draft test for the option to select an objective """
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A, bounds=(-1,1))
        def obj1_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        model.obj1 = Objective(rule=obj1_rule)
        def obj2_rule(model):
            expr = 0
            tmp=-1
            for i in model.A:
                expr += tmp*i*model.x[i]
                tmp *= -1
            return expr
        model.obj2 = Objective(rule=obj2_rule)
        instance = model.create()
        opt = SolverFactory('glpk', keepfiles=True)
        results = opt.solve(instance, objective='obj2')
        results.write(filename=currdir+"solve5.out", format='json')
        self.assertMatchesJsonBaseline(currdir+"solve5.out",currdir+"solve5a.txt", tolerance=1e-4)

if __name__ == "__main__":
    unittest.main()

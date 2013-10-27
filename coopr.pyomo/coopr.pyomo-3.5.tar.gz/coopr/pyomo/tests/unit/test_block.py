#
# Unit Tests for Elements of a Block
#

import os
import sys
from os.path import abspath, dirname, join

currdir = dirname( abspath(__file__) )

from coopr.pyomo import *
from coopr.opt import *
import pyutilib.th as unittest
import pyutilib.services

class TestGenerators(unittest.TestCase):
    
    @ unittest.nottest
    def generate_model(self):
        #
        # ** DO NOT modify the model below without updating the
        # subcomponent_lists and subcomponent_data_lists with the correct
        # declaration orders
        #

        model = ConcreteModel()
        model.q = Set(initialize=[1,2])
        model.Q = Set(model.q,initialize=[1,2])
        model.x = Var(initialize=-1)
        model.X = Var(model.q,initialize=-1)
        model.e = Expression(initialize=-1)
        model.E = Expression(model.q,initialize=-1)
        model.p = Param(mutable=True,initialize=-1)
        model.P = Param(model.q,mutable=True,initialize=-1)
        model.o = Objective(expr=-1)
        model.O = Objective(model.q, expr=lambda model,i: -1)
        model.c = Constraint(expr=model.x>=-1)
        model.C = Constraint(model.q, expr=lambda model,i: model.X[i]>=-1)
        model.sos = SOSConstraint(var=model.X, set=model.q, sos=1)
        model.SOS = SOSConstraint(model.q, var=model.X, set=model.Q, sos=1)
        model.s = Suffix()

        
        model.b = Block()
        model.b.q = Set(initialize=[1,2])
        model.b.Q = Set(model.b.q,initialize=[1,2])
        model.b.x = Var(initialize=0)
        model.b.X = Var(model.b.q,initialize=0)
        model.b.e = Expression(initialize=0)
        model.b.E = Expression(model.b.q,initialize=0)
        model.b.p = Param(mutable=True,initialize=0)
        model.b.P = Param(model.b.q,mutable=True,initialize=0)
        model.b.o = Objective(expr=0)
        model.b.O = Objective(model.b.q, expr=lambda b,i: 0)
        model.b.c = Constraint(expr=model.b.x>=0)
        model.b.C = Constraint(model.b.q, expr=lambda b,i: b.X[i]>=0)
        model.b.sos = SOSConstraint(var=model.b.X, set=model.b.q, sos=1)
        model.b.SOS = SOSConstraint(model.b.q, var=model.b.X, set=model.b.Q, sos=1)
        model.b.s = Suffix()
        model.b.subcomponent_lists = {}
        model.b.subcomponent_data_lists = {}
        model.b.subcomponent_lists[Set] = [model.b.q, model.b.Q]
        model.b.subcomponent_data_lists[Set] = [model.b.q, model.b.Q[1], model.b.Q[2]]
        model.b.subcomponent_lists[Var] = [model.b.x, model.b.X]
        model.b.subcomponent_data_lists[Var] = [model.b.x, model.b.X[1], model.b.X[2]]
        model.b.subcomponent_lists[Expression] = [model.b.e, model.b.E]
        model.b.subcomponent_data_lists[Expression] = [model.b.e, model.b.E[1], model.b.E[2]]
        model.b.subcomponent_lists[Param] = [model.b.p, model.b.P]
        model.b.subcomponent_data_lists[Param] = [model.b.p, model.b.P[1], model.b.P[2]]
        model.b.subcomponent_lists[Objective] = [model.b.o, model.b.O]
        model.b.subcomponent_data_lists[Objective] = [model.b.o, model.b.O[1], model.b.O[2]]
        model.b.subcomponent_lists[Constraint] = [model.b.c, model.b.C]
        model.b.subcomponent_data_lists[Constraint] = [model.b.c, model.b.C[1], model.b.C[2]]
        #model.b.subcomponent_lists[SOSConstraint] = [model.b.sos, model.b.SOS]
        #model.b.subcomponent_data_lists[SOSConstraint] = [model.b.sos, model.b.SOS[1], model.b.SOS[2]]
        model.b.subcomponent_lists[Suffix] = [model.b.s]
        model.b.subcomponent_data_lists[Suffix] = [model.b.s]
        model.b.subcomponent_lists[Block] = []
        model.b.subcomponent_data_lists[Block] = []

        def B_rule(block,i):
            block.q = Set(initialize=[1,2])
            block.Q = Set(block.q,initialize=[1,2])
            block.x = Var(initialize=i)
            block.X = Var(block.q,initialize=i)
            block.e = Expression(initialize=i)
            block.E = Expression(block.q,initialize=i)
            block.p = Param(mutable=True,initialize=i)
            block.P = Param(block.q,mutable=True,initialize=i)
            block.o = Objective(expr=i)
            block.O = Objective(block.q, expr=lambda b,i: i)
            block.c = Constraint(expr=block.x>=i)
            block.C = Constraint(block.q, expr=lambda b,i: b.X[i]>=i)
            block.sos = SOSConstraint(var=block.X, set=block.q, sos=1)
            block.SOS = SOSConstraint(block.q, var=block.X, set=block.Q, sos=1)
            block.s = Suffix()
            block.subcomponent_lists = {}
            block.subcomponent_data_lists = {}
            block.subcomponent_lists[Set] = [block.q, block.Q]
            block.subcomponent_data_lists[Set] = [block.q, block.Q[1], block.Q[2]]
            block.subcomponent_lists[Var] = [block.x, block.X]
            block.subcomponent_data_lists[Var] = [block.x, block.X[1], block.X[2]]
            block.subcomponent_lists[Expression] = [block.e, block.E]
            block.subcomponent_data_lists[Expression] = [block.e, block.E[1], block.E[2]]
            block.subcomponent_lists[Param] = [block.p, block.P]
            block.subcomponent_data_lists[Param] = [block.p, block.P[1], block.P[2]]
            block.subcomponent_lists[Objective] = [block.o, block.O]
            block.subcomponent_data_lists[Objective] = [block.o, block.O[1], block.O[2]]
            block.subcomponent_lists[Constraint] = [block.c, block.C]
            block.subcomponent_data_lists[Constraint] = [block.c, block.C[1], block.C[2]]
            #block.subcomponent_lists[SOSConstraint] = [block.sos, block.SOS]
            #block.subcomponent_data_lists[SOSConstraint] = [block.sos, block.SOS[1], block.SOS[2]]
            block.subcomponent_lists[Suffix] = [block.s]
            block.subcomponent_data_lists[Suffix] = [block.s]
            block.subcomponent_lists[Block] = []
            block.subcomponent_data_lists[Block] = []
        model.B = Block(model.q,rule=B_rule)
        
        model.subcomponent_lists = {}
        model.subcomponent_data_lists = {}
        model.subcomponent_lists[Set] = [model.q, model.Q]
        model.subcomponent_data_lists[Set] = [model.q, model.Q[1], model.Q[2]]
        model.subcomponent_lists[Var] = [model.x, model.X]
        model.subcomponent_data_lists[Var] = [model.x, model.X[1], model.X[2]]
        model.subcomponent_lists[Expression] = [model.e, model.E]
        model.subcomponent_data_lists[Expression] = [model.e, model.E[1], model.E[2]]
        model.subcomponent_lists[Param] = [model.p, model.P]
        model.subcomponent_data_lists[Param] = [model.p, model.P[1], model.P[2]]
        model.subcomponent_lists[Objective] = [model.o, model.O]
        model.subcomponent_data_lists[Objective] = [model.o, model.O[1], model.O[2]]
        model.subcomponent_lists[Constraint] = [model.c, model.C]
        model.subcomponent_data_lists[Constraint] = [model.c, model.C[1], model.C[2]]
        #model.subcomponent_lists[SOSConstraint] = [model.sos, model.SOS]
        #model.subcomponent_data_lists[SOSConstraint] = [model.sos, model.SOS[1], model.SOS[2]]
        model.subcomponent_lists[Suffix] = [model.s]
        model.subcomponent_data_lists[Suffix] = [model.s]
        model.subcomponent_lists[Block] = [model.b, model.B]
        model.subcomponent_data_lists[Block] = [model.b, model.B[1], model.B[2]]
        
        return model

    @ unittest.nottest
    def generator_test(self, ctype):

        model = self.generate_model()

        for block in model.all_blocks(sort_by_keys=True):

            # Non-nested active_subcomponents_generator
            generator = None
            try:
                generator = list(active_subcomponents_generator(block, ctype))
            except:
                if issubclass(ctype, Component):
                    self.fail("active_subcomponents_generator failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("subcomponents_generator should have failed with ctype %s" % ctype)
                self.assertEqual([id(comp) for comp in generator],
                                 [id(comp) for comp in block.subcomponent_lists[ctype]])
            
            # Non-nested subcomponents_generator
            generator = None
            try:
                generator = list(subcomponents_generator(block, ctype))
            except:
                if issubclass(ctype, Component):
                    self.fail("subcomponents_generator failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("subcomponents_generator should have failed with ctype %s" % ctype)
                self.assertEqual([id(comp) for comp in generator],
                                 [id(comp) for comp in block.subcomponent_lists[ctype]])

            # Non-nested active_subcomponents_data_generator, sort_by_keys=True
            generator = None
            try:
                generator = list(active_subcomponents_data_generator(block, ctype, sort_by_keys=True))
            except:
                if issubclass(ctype, Component):
                    self.fail("active_subcomponents_data_generator(sort_by_keys=True) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("active_subcomponents_data_generator(sort_by_keys=True) should have failed with ctype %s" % ctype)
                self.assertEqual([id(comp) for comp in generator],
                                 [id(comp) for comp in block.subcomponent_data_lists[ctype]])

            # Non-nested active_subcomponents_data_generator, sort_by_keys=False
            generator = None
            try:
                generator = list(active_subcomponents_data_generator(block, ctype, sort_by_keys=False))
            except:
                if issubclass(ctype, Component):
                    self.fail("active_subcomponents_data_generator(sort_by_keys=False) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("active_subcomponents_data_generator(sort_by_keys=False) should have failed with ctype %s" % ctype)
                self.assertEqual(sorted([id(comp) for comp in generator]),
                                 sorted([id(comp) for comp in block.subcomponent_data_lists[ctype]]))

            # Non-nested sucomponents_data_generator, sort_by_keys=True
            generator = None
            try:
                generator = list(subcomponents_data_generator(block, ctype, sort_by_keys=True))
            except:
                if issubclass(ctype, Component):
                    self.fail("subcomponents_data_generator(sort_by_keys=True) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("subcomponents_data_generator(sort_by_keys=True) should have failed with ctype %s" % ctype)
                    self.assertEqual([id(comp) for comp in generator],
                                     [id(comp) for comp in block.subcomponent_data_lists[ctype]])

            # Non-nested subcomponents_data_generator, sort_by_keys=False
            generator = None
            try:
                generator = list(subcomponents_data_generator(block, ctype, sort_by_keys=False))
            except:
                if issubclass(ctype, Component):
                    self.fail("subcomponents_data_generator(sort_by_keys=False) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("subcomponents_data_generator(sort_by_keys=False) should have failed with ctype %s" % ctype)
                self.assertEqual(sorted([id(comp) for comp in generator]),
                                 sorted([id(comp) for comp in block.subcomponent_data_lists[ctype]]))

    def test_Objective(self):
        self.generator_test(Objective)

    def test_Expression(self):
        self.generator_test(Expression)

    def test_Suffix(self):
        self.generator_test(Suffix)

    def test_Constraint(self):
        self.generator_test(Constraint)

    def test_Param(self):
        self.generator_test(Param)

    def test_Var(self):
        self.generator_test(Var)

    #def test_Set(self):
    #    self.generator_test(Set)

    #def test_SOSConstraint(self):
    #    self.generator_test(Set)

    def test_Block(self):

        self.generator_test(Block)

        model = self.generate_model()

        # sorted all_blocks
        self.assertEqual([id(comp) for comp in model.all_blocks(sort_by_keys=True)],
                         [id(comp) for comp in [model,]+model.subcomponent_data_lists[Block]])

        # unsorted all_blocks
        self.assertEqual(sorted([id(comp) for comp in model.all_blocks(sort_by_keys=False)]),
                         sorted([id(comp) for comp in [model,]+model.subcomponent_data_lists[Block]]))

        
class Test(unittest.TestCase):

    def setUp(self):
        #
        # Create block
        #
        self.block = Block()
        self.block.construct()

    def tearDown(self):
        if os.path.exists("unknown.lp"):
            os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_clear_attribute(self):
        """ Coverage of the _clear_attribute method """
        obj = Set()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Var()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Param()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Objective()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Constraint()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Set()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

    def test_set_attr(self):
        self.block.x = Param(mutable=True)
        self.block.x = 5
        self.assertEqual(value(self.block.x), 5)
        self.block.x = 6
        self.assertEqual(value(self.block.x), 6)
        try:
            self.block.x = None
            self.fail("Expected exception assigning None to domain Any")
        except ValueError:
            pass

    def test_display(self):
        self.block.A = RangeSet(1,4)
        self.block.x = Var(self.block.A, bounds=(-1,1))
        def obj_rule(block):
            return summation(block.x)
        self.block.obj = Objective(rule=obj_rule)
        #self.instance = self.block.create()
        #self.block.pprint()
        #self.block.display()

    def Xtest_write2(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            return (1, model.x[1]+model.x[2], 2)
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        self.instance.write()

    def Xtest_write3(self):
        """Test that the summation works correctly, even though param 'w' has a default value"""
        self.model.J = RangeSet(1,4)
        self.model.w=Param(self.model.J, default=4)
        self.model.x=Var(self.model.J)
        def obj_rule(instance):
            return summation(instance.x, instance.w)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj[None].expr._args), 4)

    def Xtest_solve1(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        #self.instance.pprint()
        opt = SolverFactory('glpk')
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1.txt"))
        #
        def d_rule(model):
            return model.x[1] > 0
        self.model.d = Constraint(rule=d_rule)
        self.model.d.deactivate()
        self.instance = self.model.create()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1.txt")
        #
        self.model.d.activate()
        self.instance = self.model.create()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1a.txt"))
        #
        self.model.d.deactivate()
        def e_rule(i, model):
            return model.x[i] > 0
        self.model.e = Constraint(self.model.A, rule=e_rule)
        self.instance = self.model.create()
        for i in self.instance.A:
            self.instance.e[i].deactivate()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1b.txt"))

    def Xtest_load1(self):
        """Testing loading of vector solutions"""
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        ans = [0.75]*4
        self.instance.load(ans)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1c.txt"))

    def Xtest_solve3(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve3.txt"))

    def Xtest_solve4(self):
        if not pyutilib.services.registered_executable("glpsol"):
            return
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        #self.instance.pprint()
        opt = SolverFactory('glpk', keepfiles=True)
        solutions = opt.solve(self.instance)
        self.instance.load(solutions.solution(0))
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1.txt"))

if __name__ == "__main__":
    unittest.main()

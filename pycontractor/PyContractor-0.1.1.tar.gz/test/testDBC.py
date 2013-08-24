from unittest import TestCase
import PyContractor.PyContractor as dbc

class TesterClass(object):

    def division(self, a, b):
        dbc.PyContractor.require(b != 0, "Divisor must be non-zero")

    def stackNotEmpty(self):
        stack = [22]
        stack.pop()
        dbc.PyContractor.ensure(stack, 'Stack must not be left empty')

    def assertStatement(self, n):
        dbc.PyContractor.assertExpression(n == 1, 'Assertion failed')

    def assertInvariant(self, n):
            dbc.PyContractor.invariant(n == 1, 'Assertion failed')

    def evaluateString(self, string1, string2):
        st = string1 + string2
        dbc.PyContractor.require_not_blank(st, 'String concatenation is blank')

class testBaseDBC(TestCase):

    def setUp(self):
        self.tester = TesterClass()

    def testRequire(self):
        with self.assertRaises(Exception):
            self.tester.division(3,0)

    def testEnsure(self):
        with self.assertRaises(Exception):
            self.tester.stackNotEmpty()

    def testAssertCorrectException(self):
        self.tester.assertStatement(1)

    def testAssertInvariant(self):
            self.tester.assertInvariant(1)

    def testAssertIncorrectException(self):
        with self.assertRaises(Exception):
            self.tester.assertStatement(34)

    def testStringConcat(self):
        self.tester.evaluateString('d','d')

    def testStringConcatNull(self):
        with self.assertRaises(Exception):
            self.tester.evaluateString('','')

    def testFail(self):
        with self.assertRaises(Exception):
            dbc.PyContractor.fail("Failed test")


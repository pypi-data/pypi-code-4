#!/usr/bin/env python

import PyStatistics as PS
import unittest


class MathFunctions(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(3.141592653589793 , PS.PI)
        self.assertAlmostEqual(2.718281828459045, PS.E)
        self.assertAlmostEqual(1.4142135623730951, PS.SQRT2)

    def test_factorial(self):
        self.assertEqual(1, PS.factorial(0))
        self.assertEqual(1, PS.factorial(1))
        self.assertEqual(2, PS.factorial(2))
        self.assertEqual(6, PS.factorial(3))
        self.assertEqual(24, PS.factorial(4))
        self.assertEqual(120, PS.factorial(5))
        self.assertRaises(PS.InvalidParameter, PS.factorial, -1)

    def test_factorial_approximate(self):
        self.assertAlmostEqual(1.0, PS.approxfactorial(0))
        self.assertAlmostEqual(1.0, PS.approxfactorial(1))
        self.assertAlmostEqual(2.0, PS.approxfactorial(2))
        self.assertAlmostEqual(6.0, PS.approxfactorial(3))
        self.assertAlmostEqual(24.0, PS.approxfactorial(4))
        self.assertAlmostEqual(120.0, PS.approxfactorial(5))
        self.assertRaises(PS.InvalidParameter, PS.approxfactorial, -1)

    def test_isprime(self):
        self.assertEqual(False, PS.isprime(-2))
        self.assertEqual(False, PS.isprime(-1))
        self.assertEqual(False, PS.isprime(0))
        self.assertEqual(False, PS.isprime(1))
        self.assertEqual(True, PS.isprime(2))
        self.assertEqual(True, PS.isprime(3))
        self.assertEqual(False, PS.isprime(4L))
        self.assertEqual(True, PS.isprime(5L))

    def test_primesuntil(self):
        primes = PS.primesuntil(1)
        self.assertEqual(0, len(primes))
        primes = PS.primesuntil(20)
        # string output on a vector works!
        self.assertEqual('(2, 3, 5, 7, 11, 13, 17, 19)', str(primes))

    def test_polyeval(self):
        # x^2 -3x + 2, even constructed from a python list!
        poly = PS.vector_double([2.0, -3.0, 1.0])
        self.assertAlmostEqual(12.0, PS.polyeval(poly, -2.0))
        self.assertAlmostEqual(8.75, PS.polyeval(poly, -1.5))
        self.assertAlmostEqual(2.0, PS.polyeval(poly, 0.0))
        self.assertAlmostEqual(0.0, PS.polyeval(poly, 1.0))
        self.assertAlmostEqual(-0.25, PS.polyeval(poly, 1.5))


class ProbabilityDistributions(unittest.TestCase):
    def test_exponential(self):
        # TypeError thrown when no parameters are given:
        self.assertRaises(TypeError,PS.ExponentialDistribution)
        # TypeError thrown when too many parameters given:
        self.assertRaises(TypeError,PS.ExponentialDistribution, 1, 2)
        e = PS.ExponentialDistribution(1.5)
        self.assertAlmostEqual(1.5, e.lambdaValue)
        self.assertAlmostEqual(0.0, e.pdf(-5))
        self.assertAlmostEqual(0.0008296265552217505, e.pdf(5))
        self.assertAlmostEqual(0.7768698398515702, e.cdf(1))
        self.assertAlmostEqual(0.9999999999200804, e.cdf(15.5))
        self.assertAlmostEqual(0.6666666666666666, e.expectedvalue())
        self.assertAlmostEqual(0.4444444444444444, e.variance())

    def test_gaussian(self):
        e = PS.GaussianDistribution(1500, 200.0)
        self.assertAlmostEqual(1500.0, e.mu)
        self.assertAlmostEqual(200.0, e.sigma)
        self.assertAlmostEqual(0.0, e.pdf(-5))
        self.assertAlmostEqual(0.0019947114020071634, e.pdf(1500))
        self.assertAlmostEqual(0.5, e.cdf(1500.0))
        # ~68% should fall between 1 standard deviation of the mean:
        self.assertAlmostEqual(0.6826894921370861, e.cdf(1700) - e.cdf(1300))
        self.assertAlmostEqual(1.0, e.cdf(9999999))
        self.assertAlmostEqual(1500.0, e.expectedvalue())
        self.assertAlmostEqual(40000.0, e.variance())

        expected = ('Gaussian distributed variable with:\n'
                    '  Mu: 1500\n'
                    '  Sigma: 200\n'
                    '  E(X): 1500\n'
                    '  Var(X): 40000\n')
        self.assertEqual(expected, str(e))


class DiscreteStats(unittest.TestCase):
    def test_vector_wrapper(self):
        # while we're here, let's show how the vector wrapper is very similar to a python list
        data = PS.vector_double()
        data.append(15.0)
        data.append(25.3)
        self.assertEqual(2, len(data))    # the size method got wrapped to the __len__ method
        self.assertEqual(2, data.size())  # we can still use the old method, if we're crazy
        self.assertEqual(15.0, data[0])
        self.assertEqual(25.3, data[1])

        index = 0
        for x in data:  # normal iteration works
            self.assertEqual(data[index], x)
            index += 1

        for index, x in enumerate(data):  # iteration by index, element works
            self.assertEqual(data[index], x)

        self.assertEqual(40.3, sum(data))  # if it looks like a duck...

    def test_functions(self):
        data = PS.vector_double()
        data.append(1.0)
        data.append(1.5)
        data.append(1.2)
        data.append(1.4)
        self.assertAlmostEqual(1.275, PS.mean(data))
        self.assertAlmostEqual(0.036875, PS.variance(data))


class Regressions(unittest.TestCase):
    def test_linear(self):
        x = PS.datalist()
        # almost f(x) = 2*x + 1
        # best fit is f(x) = 1.98x + 1.1
        x.addpoint(1.0, 3.0)
        x.addpoint(2.0, 5.1)
        x.addpoint(3.0, 7.2)
        x.addpoint(4.0, 8.9)
        x.addpoint(5.0, 11.0)
        answer = PS.regression(x, PS.LINEAR)
        self.assertEqual(2, len(answer))
        self.assertAlmostEqual(1.1, answer[0])
        self.assertAlmostEqual(1.98, answer[1])
        self.assertAlmostEqual(3.08, PS.polyeval(answer, 1.0))
        self.assertAlmostEqual(5.06, PS.polyeval(answer, 2.0))
        self.assertAlmostEqual(7.04, PS.polyeval(answer, 3.0))


if __name__ == "__main__":
    unittest.main()

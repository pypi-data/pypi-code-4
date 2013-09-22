import random
from math import copysign, frexp
from six.moves import xrange
from .arbitrary import Arbitrary, with_samples
from .utils import filter_possible, until_possible, unique, product
from .primitives import elements


__all__ = ['int_', 'float_']


@Arbitrary.set_for(int)
@with_samples
class int_(Arbitrary):
    """ Uniformly distributed integer from the specified range. """

    def __init__(self, low=-1 << 32, high=(1 << 32) - 1, uniform=False):
        self.low = low
        self.high = high
        self.uniform = uniform

        if not uniform:
            self.signs = list({int(copysign(1, x)) for x in [low, high]})
            maxabs = max(abs(low), abs(high))
            minabs = min(abs(low), abs(high)) if len(self.signs) == 1 else 0
            self.minlog2 = minabs.bit_length()
            self.maxlog2 = maxabs.bit_length()

    def could_generate(self, x):
        return self.low <= x <= self.high

    @until_possible
    def next_random(self):
        if self.uniform:
            return random.randint(self.low, self.high)
        else:
            log2 = random.randint(self.minlog2, self.maxlog2)
            mn = int(2 ** (log2 - 1))
            mx = 2 ** log2
            rnd = random.randint(mn, mx - 1)
            sign = random.choice(self.signs)
            rnd *= sign
            return rnd

    @unique
    @filter_possible
    def gen_serial(self):
        yield 0
        yield 1
        yield self.low
        yield self.high
        if self.low < 0 < self.high:
            for i in xrange(0, max(abs(self.low), abs(self.high))):
                yield i
                yield -i
        else:
            # sign(low) = sign(high)
            if abs(self.low) < abs(self.high):
                # |low| < |high| thus 0 < low < high
                for i in xrange(self.low, self.high):
                    yield i
            else:
                # |high| < |low| thus low < high < 0
                for i in xrange(self.high, self.low, -1):
                    yield i


    @unique
    @filter_possible
    def shrink(self, x):
        xsign = int(copysign(1, x))
        xabs = abs(x)
        yield xsign * (xabs // 2)
        yield xsign * (xabs // 10 ** 5 * 10 ** 5)
        yield xsign * (xabs // 10 ** 2 * 10 ** 2)
        if x < 0:
            yield xabs


@unique
@filter_possible
def float_shrink(self, x):
    if x < 0:
        yield -x

    if abs(x) > 2:
        yield x / 2
    if abs(x) < 0.5:
        yield x * 2

    yield round(x)
    yield round(x, 1)
    yield round(x, 2)
    yield round(x, 3)
    yield round(x, 4)


@Arbitrary.set_for(float)
@with_samples
class float_(Arbitrary):
    """ Float with significand, exponent and sign taken according to the parameters. """

    def __init__(self, low=-100, high=100, uniform=False):
        self.low = float(low)
        self.high = float(high)
        self.uniform = uniform

        signs = list({int(copysign(1, x)) for x in [low, high]})
        self.sign = elements(*signs)

        _, max_exp = frexp(max(abs(low), abs(high)))
        assert isinstance(signs, list)
        _, min_exp = frexp(min(abs(low), abs(high))) \
                         if len(signs) == 1 else None, max_exp - 40
        self.exp = int_(min_exp, max_exp)

        self.sig = int_(0, 1 << 53, uniform=True)


    def could_generate(self, x):
        return self.low <= x <= self.high

    @until_possible
    def next_random(self):
        if self.uniform:
            return random.uniform(self.low, self.high)
        else:
            sign = self.sign.next_random()
            sig = self.sig.next_random()
            exp = self.exp.next_random()
            sig_p2 = 2 ** sig.bit_length()
            sig = 1.0 * sig / sig_p2
            return sign * sig * 2.0 ** exp

    @unique
    @filter_possible
    def gen_serial(self):
        yield 0
        yield self.low
        yield self.high

        for sign, sig, exp in product(self.sign.gen_serial(),
                                      self.sig.gen_serial(),
                                      self.exp.gen_serial()):
            sig_p2 = 2 ** sig.bit_length()
            sig = 1.0 * sig / sig_p2
            yield sign * sig * 2.0 ** exp

    shrink = float_shrink

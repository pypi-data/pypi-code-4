import random
import math
from itertools import count
from six.moves import xrange
from ..arbitrary import Arbitrary
from .utils import filter_possible, unique
from .primitives import elements


__all__ = ['int_', 'float_', 'float_uniform', 'float_fraction', 'float_exp']


@Arbitrary.set_for(int)
class int_(Arbitrary):
    """ Uniformly distributed integer from the specified range. """

    def __init__(self, low=-1 << 32, high=(1 << 32) - 1):
        self.low = low
        self.high = high

    def could_generate(self, x):
        return self.low <= x <= self.high

    def next_random(self):
        return random.randint(self.low, self.high)

    @unique
    @filter_possible
    def gen_serial(self, amount):
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
        yield x // 2
        yield x // 10 ** 5 * 10 ** 5
        yield x // 10 ** 2 * 10 ** 2
        if x < 0:
            yield -x


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


class float_uniform(Arbitrary):
    """ Uniformly distributed float from the specified range. """

    def __init__(self, low=-100, high=100):
        self.low = low
        self.high = high

    def could_generate(self, x):
        return self.low <= x <= self.high

    def next_random(self):
        return random.uniform(self.low, self.high)

    @unique
    def gen_serial(self, amount):
        for p2 in count(start=0, step=-1):
            mul = 2.0 ** p2
            arb = int_(int(self.low / mul), int(self.high / mul))
            for x in arb.gen_serial(amount):
                yield x * mul

    shrink = float_shrink


@Arbitrary.set_for(float)
class float_fraction(Arbitrary):
    """ Uniformly distributed float from the specified range, representing
    a fraction with a denominator taken according to ``denom``. """

    def __init__(self, low=-100, high=100, denom=int_(1, 20)):
        self.low = low
        self.high = high
        self.denom = denom

    def could_generate(self, x):
        return self.low <= x <= self.high

    def next_random(self):
        denom = self.denom.next_random()
        nom = random.randint(denom * self.low, denom * self.high)
        return 1.0 * nom / denom

    def gen_serial(self, amount):
        seen = set()
        inner_amount = int(amount ** (1.0 / 2))

        for i, denom in enumerate(self.denom.gen_serial(inner_amount)):
            nom_arb = int_(int(denom * self.low), int(denom * self.high))

            for nom in nom_arb.gen_serial(amount):
                val = 1.0 * nom / denom
                if val not in seen:
                    yield val

                seen.add(val)
                if len(seen) >= (i + 1) * inner_amount:
                    break

    shrink = float_shrink


float_ = float_fraction


class float_exp(Arbitrary):
    """ Float with significand, exponent and sign taken according to the parameters. """

    def __init__(self,
                 sig=float_uniform(0.5, 1),
                 exp=int_(-32, 32),
                 sign=elements(1, -1)):
        self.sign = sign
        self.sig = sig
        self.exp = exp

    def could_generate(self, x):
        sig, exp = math.frexp(x)
        sign = math.copysign(1, sig)
        sig = sig / sign
        return (self.sign.could_generate(sign) and
                self.sig.could_generate(sig) and
                self.exp.could_generate(exp))

    def next_random(self):
        sign = self.sign.next_random()
        sig = self.sig.next_random()
        exp = self.exp.next_random()
        return sign * sig * 2.0 ** exp

    def gen_serial(self, amount):
        return []

    shrink = float_shrink

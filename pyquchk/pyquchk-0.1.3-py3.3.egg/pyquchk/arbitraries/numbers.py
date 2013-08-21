import random
import math
from . import Arbitrary, filter_possible, unique


class int_(Arbitrary(int)):
    def __init__(self, low=-1 << 32, high=(1 << 32) - 1):
        self.low = low
        self.high = high

    def could_generate(self, x):
        return self.low <= x <= self.high

    def __next__(self):
        return random.randint(self.low, self.high)

    @filter_possible
    def get_edgecases(self):
        return {self.low, 0, 1, self.high}

    @unique
    def shrink(self, x):
        yield x // 2
        yield x // 10**5 * 10**5
        yield x // 10**2 * 10**2
        if x < 0:
            yield -x


class float_(Arbitrary(float)):
    def __init__(self, low=float(-1 << 32), high=float(1 << 32)):
        self.low = low
        self.high = high

    def could_generate(self, x):
        return self.low <= x <= self.high

    def __next__(self):
        mantissa = random.uniform(0.5, 1)
        sign = 1 if random.getrandbits(1) else -1
        exponent = random.randint(-30, 30)
        return math.ldexp(sign * mantissa, exponent)

    @filter_possible
    def get_edgecases(self):
        return {self.low, 0.0, self.high}

    @unique
    def shrink(self, x):
        if abs(x) > 2:
            yield x / 2
        if abs(x) < 0.5:
            yield x * 2
        if x < 0:
            yield -x

        yield round(x)
        yield round(x, 1)
        yield round(x, 2)
        yield round(x, 3)
        yield round(x, 4)

from . import Arbitrary, filter_possible
from .numbers import int_


class list_(Arbitrary(list)):
    def __init__(self, length=int_(0, 32), elements=int_):
        self.length = length
        self.elements = elements

    def could_generate(self, x):
        return self.length.could_generate(len(x)) and \
               all(self.elements.could_generate(el) for el in x)

    def __next__(self):
        return [next(self.elements) for _ in range(next(self.length))]

    @filter_possible
    def get_edgecases(self):
        try:
            elem = next(self.elements.get_edgecases())
        except:
            elem = next(self.elements)

        yield []
        yield [elem]
        yield [elem for _ in range(self.length.low)]
        yield [elem for _ in range(self.length.high)]

    @filter_possible
    def shrink(self, x):
        l = len(x)
        if l > 1:
            yield x[:-1]
            yield x[1:]

            yield x[:l // 3]
            yield x[l // 3:2 * l // 3]
            yield x[2 * l // 3:]

            el_gens = map(self.elements.shrink, x)
            for els in zip(*el_gens):
                yield list(els)
        elif l == 1:
            for el in self.elements.shrink(x[0]):
                yield [el]

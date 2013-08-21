from decorator import decorator
from .arbitrary import Arbitrary


@decorator
def func_to_gen(func, *args, **kwargs):
    while True:
        yield func(*args, **kwargs)


def gen_to_arb(gen_func):
    class AGen(Arbitrary):
        gen_func = gen_func

        def __next__(self):
            yield self.gen_func()

    return AGen


@decorator
def filter_possible(method, self, *args, **kwargs):
    for item in method(self, *args, **kwargs):
        if self.could_generate(item):
            yield item

@decorator
def unique(func, self, x):
    seen = {x}
    for item in func(self, x):
        if item not in seen:
            yield item
            seen.add(item)

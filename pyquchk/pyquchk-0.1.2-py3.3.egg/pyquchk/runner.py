from functools import wraps
import inspect
import itertools
import sys
import six
from .utils import optional_args
from .arbitraries import Arbitrary


def CheckError(data, cause):
    class CheckError(type(cause)):
        """Exception raised when property test fails.

        It constains the original test data for which
        the test has failed.
        """

        def __init__(self, data, cause):
            self.test_data = data
            self.cause = cause

        def __str__(self):
            msg = "test failed"
            if self.cause is not None:
                msg += " due to %s" % type(self.cause).__name__
                cause = str(self.cause)
                if cause:
                    msg += ": " + cause

            res = [msg]
            res.append("Failure encountered for data:")
            res.extend(["  %s = %s" % i for i in self.test_data.items()])
            return '\n'.join(res)

    return CheckError(data, cause)


class Runner(object):
    def __init__(self, func, args, ntests, edgecases):
        self.func = func
        self.args = args
        self.ntests = ntests
        self.edgecases = edgecases

        self.arg_arbs = {}
        for argname, value in self.args:
            if isinstance(value, type) and not issubclass(value, Arbitrary):
                # e.g. 'int', 'list' - any class with defined arbitrary_for
                value = Arbitrary.get_for(value)

            # Arbitrary instanciated above
            self.arg_arbs[argname] = value


    def generate_data(self):
        if self.edgecases is not False:
            arg_edgecases = [v.get_edgecases() for k, v in self.arg_arbs.items()]
            # use 'product' to run through all edgecases
            for values in itertools.product(*arg_edgecases):
                kwargs = dict(zip(self.arg_arbs.keys(), values))
                yield kwargs

        if self.edgecases is not True:
            for _ in range(self.ntests):
                kwargs = {k: next(v) for k, v in self.arg_arbs.items()}
                yield kwargs


    def full_shrink(self, data):
        changed = True
        while changed:
            changed = False
            shr_gens = [self.arg_arbs[k].shrink(data[k]) for k in self.arg_arbs.keys()]
            for shr_values in itertools.product(*shr_gens):
                shr_data = dict(zip(self.arg_arbs.keys(), shr_values))
                try:
                    self.func(**shr_data)
                except Exception as e:
                    data = shr_data
                    changed = True
        return data


    def __call__(self):
        for kwargs in self.generate_data():
            try:
                self.func(**kwargs)
            except Exception as e:
                kwargs = self.full_shrink(kwargs)
                _, _, traceback = sys.exc_info()
                ei = CheckError(kwargs, e)
                six.reraise(type(ei), ei, traceback)


@optional_args
class qc(object):
    def __init__(self, ntests=100, edgecases=None):
        self.ntests = ntests
        self.edgecases = edgecases

        frames = inspect.stack()
        self.func_is_method = any(fr[4][0].strip().startswith('class ')
                                  for fr in frames
                                  if fr and fr[4])

    def __call__(self, func):
        argspec = inspect.getargspec(func)
        argnames = list(argspec.args or [])
        defaults = list(argspec.defaults or [])
        defaults = [None] * (len(argnames) - len(defaults)) + defaults
        args = list(zip(argnames, defaults))

        if any(d is None for a, d in args):
            raise TypeError("unbound variables: %s" % ', '.join(a for a, d in args if d is None))

        runner = Runner(func, args, self.ntests, self.edgecases)

        if self.func_is_method:
            wrapped = lambda _self: runner()
        else:
            wrapped = lambda: runner()

        wraps(func)(wrapped)
        wrapped.__test__ = True
        return wrapped

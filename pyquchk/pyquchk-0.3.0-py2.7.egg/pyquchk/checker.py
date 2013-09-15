import itertools
import sys
import six
from .arbitraries.arbitrary import Arbitrary


__all__ = ['for_all', 'Result', 'ReturnedFalse', 'CheckError']


class CheckError(Exception):
    """ Raised when a test which uses :func:`.qc` decorator fails.

    It contains the original test data for which the test has failed, and
    the exception raised by the tested function.
    Actually, a :exc:`CheckError` instance is always also an instance of the
    exception raised by the tested function, so you can except it as usually.
    """

    #: Data which caused the function to raise an exception
    test_data = None
    #: Exception raised by the function, or :exc:`ReturnedFalse` if function
    #: returned ``False``
    cause = None


def get_CheckError(data, cause):
    class CheckError_(CheckError, type(cause)):
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
            res += ["  %s = %s" % i for i in sorted(self.test_data.items())]
            return '\n'.join(res)

    CheckError_.__name__ = 'CheckError'
    return CheckError_(data, cause)


class ReturnedFalse(Exception):
    """ Automatically raised when the tested function returns a value which
    evaluates to a :mod:`bool` ``False``.
    """

    def __init__(self, retval):
        #: Exact value returned by the function (evaluates to a ``False`` :mod:`bool` value)
        self.retval = retval

    def __str__(self):
        return 'function returned %r' % self.retval


class Result(object):
    """ Represent the result of performed testing (returned by :func:`for_all`).
    """

    def __init__(self,
                 verdict, passed, datas,
                 data=None, exception=None, traceback=None):
        #: ``'OK'`` if passed and ``'FAIL'`` if not
        self.verdict = verdict
        #: ``True`` if passed and ``False`` if not (opposite to :attr:`failed`)
        self.passed = passed
        #: ``False`` if passed and ``True`` if not (opposite to :attr:`passed`)
        self.failed = not passed
        #: List of all the data values generated during the test run
        self.datas = datas
        #: Data on which the tested function failed (as a :mod:`dict`),
        #: or ``None`` if passed
        self.data = data
        #: Exception raised by the function, or :exc:`ReturnedFalse` if function
        #: returned ``False``, or ``None`` if passed
        self.exception = exception
        #: Exception traceback, or ``None`` if passed
        self.traceback = traceback

    @classmethod
    def ok(cls, datas):
        return Result('OK', True, datas)

    @classmethod
    def fail(cls, datas, data, exception, traceback):
        return Result('FAIL', False, datas, data, exception, traceback)

    def reraise(self):
        exception = get_CheckError(self.data, self.exception)
        six.reraise(type(exception), exception, self.traceback)

    def __bool__(self):
        """ Return :attr:`passed`, used to interprete as a :mod:`bool` value.
        """
        return self.passed

    __nonzero__ = __bool__


class Checker(object):
    def __init__(self, func, args, ntests, ignore_return=False):
        self.func = func
        self.args = args
        self.ntests = ntests
        self.ignore_return = ignore_return

        self.arg_arbs = {}
        for argname, value in self.args.items():
            if isinstance(value, type) and not issubclass(value, Arbitrary):
                # e.g. 'int', 'list' - any class with defined arbitrary_for
                value = Arbitrary.get_for(value)

            # Arbitrary instanciated above
            self.arg_arbs[argname] = value


    def generate_data(self):
        each_amount = int(self.ntests ** (1.0 / len(self.arg_arbs)))
        serial_data = [v.gen_serial(each_amount)
                       for k, v in self.arg_arbs.items()]

        for values in itertools.product(*serial_data):
            kwargs = dict(zip(self.arg_arbs.keys(), values))
            yield kwargs

        for _ in range(self.ntests):
            kwargs = {k: v.next_random() for k, v in self.arg_arbs.items()}
            yield kwargs


    def eval_func(self, data):
        func_res = self.func(**data)
        if not self.ignore_return and not func_res:
            raise ReturnedFalse(func_res)


    def full_shrink(self, data):
        changed = True
        while changed:
            changed = False
            shr_gens = [self.arg_arbs[k].shrink(data[k])
                        for k in self.arg_arbs.keys()]
            for shr_values in itertools.product(*shr_gens):
                shr_data = dict(zip(self.arg_arbs.keys(), shr_values))
                try:
                    self.eval_func(shr_data)
                except Exception as e:
                    data = shr_data
                    changed = True
        return data


    def for_all(self):
        datas = []
        for kwargs in self.generate_data():
            datas.append(kwargs)
            try:
                self.eval_func(kwargs)
            except Exception as e:
                kwargs = self.full_shrink(kwargs)
                try:
                    self.eval_func(kwargs)
                except Exception as e:
                    _, _, traceback = sys.exc_info()
                    return Result.fail(datas, kwargs, e, traceback)

        return Result.ok(datas)


def for_all(func, _ntests=100, **kwargs):
    """ Test the function ``func`` on ``_ntests`` tests.

    For usage examples see :ref:`property-checking`.

    :param _ntests: number of tests
    :param kwargs: function arguments specification
    :returns: information about the tests run
    :rtype: :class:`Result`
    """
    return Checker(func, kwargs, _ntests).for_all()

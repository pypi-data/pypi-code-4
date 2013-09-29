import sys
from warnings import warn
import six
from .arbitraries.arbitrary import get_arbitrary
from .arbitraries.sequences import dict_fixkeys


__all__ = ['for_all', 'Result', 'ReturnedFalse', 'CheckError',
           'AssumptionError', 'assume']


class AssumptionError(Exception):
    pass


def assume(condition):
    if not condition:
        raise AssumptionError


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


def get_CheckError(data, noshrink_data, cause):
    class CheckError_(CheckError, type(cause)):
        def __init__(self, data, noshrink_data, cause):
            self.test_data = data
            self.noshrink_data = noshrink_data
            self.cause = cause

        def __str__(self):
            msg = "test failed"
            if self.cause is not None:
                msg += " due to %s" % type(self.cause).__name__
                cause = str(self.cause)
                if cause:
                    msg += ": " + cause

            res = [msg]
            res.append('')
            res.append("Failure encountered for data:")
            res += ["  %s = %r" % i for i in sorted(self.test_data.items())]
            res.append('')
            res.append("Before shrinking:")
            res += ["  %s = %r" % i for i in sorted(self.noshrink_data.items())]
            return '\n'.join(res)

    CheckError_.__name__ = 'CheckError'
    return CheckError_(data, noshrink_data, cause)


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
                 data=None, noshrink_data=None, exception=None, traceback=None):
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
        #: Same as :attr:`data`, but before shrinking.
        self.noshrink_data = noshrink_data
        #: Exception raised by the function, or :exc:`ReturnedFalse` if function
        #: returned ``False``, or ``None`` if passed
        self.exception = exception
        #: Exception traceback, or ``None`` if passed
        self.traceback = traceback

    @classmethod
    def ok(cls, datas):
        return Result('OK', True, datas)

    @classmethod
    def fail(cls, datas, data, noshrink_data, exception, traceback):
        return Result('FAIL', False,
                      datas, data, noshrink_data,
                      exception, traceback)

    def reraise(self):
        exception = get_CheckError(self.data, self.noshrink_data,
                                   self.exception)
        six.reraise(type(exception), exception, self.traceback)

    def __bool__(self):
        """ Return :attr:`passed`, used to interprete as a :mod:`bool` value.
        """
        return self.passed

    __nonzero__ = __bool__


class Checker(object):
    def __init__(self, func, args, ntests, nshrinks, nassume, ignore_return=False):
        self.func = func
        self.args = args
        self.ntests = ntests or 500
        self.nshrinks = nshrinks or 10000
        self.nassume = nassume or 10000
        self.ignore_return = ignore_return

        arg_arbs = {argname: get_arbitrary(self.args[argname])
                    for argname in self.args}
        self.arb = dict_fixkeys(**arg_arbs)


    def eval_func(self, data):
        func_res = self.func(**data)
        if not self.ignore_return and not func_res:
            raise ReturnedFalse(func_res)


    def full_shrink(self, kwargs):
        n = 0
        while n < self.nshrinks:
            for shr_kwargs in self.arb.shrink(kwargs):
                n += 1
                try:
                    self.eval_func(shr_kwargs)
                except AssumptionError:
                    continue
                except Exception as e:
                    kwargs = shr_kwargs
                    break
                if n > self.nshrinks:
                    break
            else:
                break
        else:
            warn('Shrink did not stop after %d iterations.' % self.nshrinks)
        return kwargs


    def for_all(self):
        gen_serial = self.arb.gen_serial()

        def generate(n):
            if n < self.ntests / 2:
                try:
                    return next(gen_serial)
                except StopIteration:
                    return self.arb.next_random()
            else:
                return self.arb.next_random()

        datas = []
        n = 0
        assume_fail_cnt = 0
        while n < self.ntests:
            kwargs = generate(n)
            datas.append(kwargs)
            try:
                self.eval_func(kwargs)
            except AssumptionError:
                del datas[-1]
                assume_fail_cnt += 1
                if assume_fail_cnt > self.nassume:
                    raise RuntimeError(
                        'Could not satisfy assume() after %d of test cases.' % self.nassume)
                continue
            except Exception as e:
                shrinked_kwargs = self.full_shrink(kwargs)
                try:
                    self.eval_func(shrinked_kwargs)
                except Exception as e:
                    _, _, traceback = sys.exc_info()
                    return Result.fail(datas, shrinked_kwargs, kwargs, e,
                                       traceback)
            n += 1

        return Result.ok(datas)


def for_all(func, **kwargs):
    """ for_all(func, ntests=None, nshrinks=None, nassume=None)
    Test the function ``func`` on ``_ntests`` tests.

    For usage examples see :ref:`property-checking`.

    :param kwargs: function arguments specification
    :returns: information about the tests run
    :rtype: :class:`Result`
    """
    ntests = kwargs.get('ntests', None)
    nshrinks = kwargs.get('nshrinks', None)
    nassume = kwargs.get('nassume', None)
    return Checker(func, kwargs, ntests, nshrinks, nassume).for_all()

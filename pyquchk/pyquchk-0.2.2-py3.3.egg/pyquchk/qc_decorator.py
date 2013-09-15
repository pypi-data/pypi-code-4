from functools import wraps
import inspect
from .checker import Checker
from .utils import optional_args


@optional_args
def qc(ntests=100):
    """ qc(ntests=100)
    Decorator for a test function.

    For usage examples see :ref:`creating-tests`.

    :param ntests: number of tests
    """

    frames = inspect.stack()
    func_is_method = any(fr[4][0].strip().startswith('class ')
                         for fr in frames
                         if fr and fr[4])

    def wrapper(func):
        argspec = inspect.getargspec(func)
        argnames = list(argspec.args or [])
        defaults = list(argspec.defaults or [])
        defaults = [None] * (len(argnames) - len(defaults)) + defaults
        args = dict(zip(argnames, defaults))

        if any(args[a] is None for a in args):
            raise TypeError('unbound variables: %s' %
                            ', '.join(a for a in args if args[a] is None))

        checker = Checker(func, args, ntests, ignore_return=True)

        def wrapped(*args):
            if not (len(args) == 0 or len(args) == 1 and func_is_method):
                raise ValueError('not expecting any arguments')

            result = checker.for_all()
            if result.failed:
                result.reraise()

        wraps(func)(wrapped)
        wrapped.__test__ = True
        return wrapped

    return wrapper

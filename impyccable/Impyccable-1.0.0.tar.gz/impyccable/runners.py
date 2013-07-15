"""Test runner."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'


class _Arger(object):
    """
    Stores argument generators and when called returns a set of arguments from
    those generators.
    """
    def __init__(self, args, kwargs):
        self._args = args
        self._kwargs = kwargs

    def args(self):
        """
        Returns an argument list from stored generators.
        """
        return [next(arg) for arg in self._args]

    def kwargs(self):
        """
        Returns a keyword argument dictionary from stored generators.
        """
        return {kw: next(arg) for kw, arg in self._kwargs.items()}


class Runner(object):
    """
    Stores a given function and argument generators to execute when asked.
    """
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = _Arger(args, kwargs)

    def __call__(self, runs=10):
        """
        Call the stored function with arguments pulled from generates with
        optional repetition.
        """
        for _ in range(runs):
            self.func(*self.args.args(), **self.args.kwargs())


class Impyccable(object):
    """
    A function decorator to provide Impyccable testing and takes generator
    arguments corrosponding to the functions paramaters. All arguments will be
    passed on in order along with all keywords to the decorated function.
    However the number of runs can be defined by giving the decorator an
    integer with the keyword "runs" without which will default to 10 runs.

    Once decorated the function may be called without arguments but with an
    optional integer to repeat the call to the underlying fuction from new
    values from the generators.
    """
    def __init__(self, *args, **kwargs):
        self.runs = kwargs.pop("runs", 10)
        self.args = _Arger(args, kwargs)

    def __call__(self, func):
        def Wrapped(*args, **kwargs):
            """
            Calls the wrapped function with optional repition using stored
            argument data generators.
            """
            runs = kwargs.pop("runs", self.runs)
            for _ in range(runs):
                func(*(list(args)+self.args.args()), **self.args.kwargs())
        Wrapped.__doc__ = func.__doc__
        Wrapped.__name__ = func.__name__
        return Wrapped

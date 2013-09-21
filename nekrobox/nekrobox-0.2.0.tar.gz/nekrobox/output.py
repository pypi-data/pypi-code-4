import sys
from contextlib import contextmanager
from functools import wraps


def get_filelike(filepath=None):
    """
    Convert a filepath into a, hopefully, appropriate file like object.
    
    If ``filepath`` is ``None`` then a null file like object will be returned that
    be written to but does nothing.

    If ``filepath`` is a string then a file object will be opened using
    ``filepath`` as the path to the file.

    Otherwise this function will just return the inputted ``filepath`` in the
    hope that it is file like enough.
    """
    if not filepath:
        class Devnull(object):
            def write(self, _): pass
        return Devnull()
    elif isinstance(filepath, str):
        return open(filepath, 'w')
    else:
        return filepath


@contextmanager
def pipe_stdout(filepath=None):
    """
    A context manager that pipes ``stdout`` to ``filepath`` after it is passed
    through :py:func:`get_filelike`.

    This can be used like so::
    >>> with pipe_stdout():
    >>>     print("This will go no where!")
    """
    sys.stdout = _get_filelike(filepath)
    yield
    sys.stdout = sys.__stdout__


@contextmanager
def pipe_stderr(filepath=None):
    """
    A context manager that pipes ``stderr`` to ``filepath`` after it is passed
    through :py:func:`get_filelike`.

    This can be used similarly to :py:func:`pipe_stdout`.
    """
    sys.stderr = _get_filelike(filepath)
    yield
    sys.stderr = sys.__stderr__


@contextmanager
def pipe_std(filepath=None):
    """
    A context manager that pipes ``stdout`` and ``stderr`` to ``filepath``
    after it is passed through :py:func:`get_filelike`.

    This can be used similarly to :py:func:`pipe_stdout`.
    """
    output = _get_filelike(filepath)
    sys.stdout = output
    sys.stderr = output
    yield
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def redirect_stdout(filepath=None):
    """
    A function wrapper that pipes ``stdout`` to ``filepath`` after it is passed
    through :py:func:`get_filelike`.

    This can be used on method or functions::
    >>> @redirect_stdout():
    >>> def foo():
    >>>     print("This will go no where!")
    """
    def _wrap(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with pipe_stdout(filepath):
                function(*args, **kwargs)
        return wrapper
    return _wrap


def redirect_stderr(filepath=None):
    """
    A function wrapper that pipes ``stderr`` to ``filepath`` after it is passed
    through :py:func:`get_filelike`.

    This can be used the same way as :py:func:`redirect_stdout`.
    """
    def _wrap(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with pipe_stderr(filepath):
                function(*args, **kwargs)
        return wrapper
    return _wrap


def redirect_std(filepath=None):
    """
    A function wrapper that pipes ``stdout`` and ``stderr`` to ``filepath``
    after it is passed through :py:func:`get_filelike`.

    This can be used the same way as :py:func:`redirect_stdout`.
    """
    def _wrap(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with pipe_std(filepath):
                function(*args, **kwargs)
        return wrapper
    return _wrap

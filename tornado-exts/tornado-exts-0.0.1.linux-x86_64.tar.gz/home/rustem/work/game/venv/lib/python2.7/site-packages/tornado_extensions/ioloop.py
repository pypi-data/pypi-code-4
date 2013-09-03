import tornado.ioloop
import datetime


def add_timeout(deadline, callback, ioloop=None):
    r"""Adds a timeout that will be called in `deadline` seconds.
    Not to be confused with tornado.ioloop.add_timeout()
    which accepts a timestamp or timedelta as the `deadline` argument.

    Parameters
    ----------
    deadline : int
        number denoting a unix timestamp.
    callback : callable
        callable that will be called.
    ioloop : Tornado IOLoop
        singleton instance of A level-triggered I/O loop.

    Returns
    -------
    handle : Returns a handle that may be passed to remove_timeout to cancel

    See Also
    --------
    IOLoop.add_timeout :
        www.tornadoweb.org/documentation/ioloop.html

    Notes
    -----
    This function is wrapper to `IOLoop.add_timeout` which executes original one
    in deadline since now

    Examples
    --------
    Assume that we have callable `do_smth()`, deadline is 1 second.

    >>> add_timeout(1000, do_smth)
    """
    ioloop = ioloop or tornado.ioloop.IOLoop.current()
    return ioloop.add_timeout(datetime.timedelta(seconds=deadline), callback)


def remove_timeout(handle, ioloop=None):
    ioloop = ioloop or tornado.ioloop.IOLoop.instance()
    return ioloop.remove_timeout(handle)

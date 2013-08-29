import logging
import functools

from twisted.internet import defer
from twisted.python import failure


logger = logging.getLogger(__name__)


def errbackLogger(error):
    if not isinstance(error, failure.Failure):
        logger.error("errbackLogger called not with Failure but with %s",
                     error)
        return error
    logger.error("Deferred fired errback:\n%s", error.getTraceback())
    return error


def logErrbacks(df):
    """Given a deferred, add an errback to print the error. Given anything
    else, do nothing. In either case, return the initial value."""
    if not isinstance(df, defer.Deferred):
        return df
    df.addErrback(errbackLogger)
    return df


def logsErrbacks(f):
    """Wrap a function such that, if it returns a Deferred, it will log
    errbacks on that Deferred."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        return logErrbacks(f(*args, **kwargs))
    return wrapped



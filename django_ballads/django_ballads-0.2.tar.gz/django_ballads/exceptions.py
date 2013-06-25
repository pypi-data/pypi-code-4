"""
Exceptions used to control and report on ballad rollbacks.
"""

class BalladException(Exception):
    """
    Something went wrong during ballad rollback.

    The attribute exceptions will contain all things that
    went wrong during rollback. Additionally, if an exception
    caused the rollback automatically (rather than rollback
    being called on the ballad), the (type, value, traceback)
    triple will be available as the cause attribute. If not,
    it will be None.
    """
    def __init__(self, exceptions, cause=None):
        super(BalladException, self).__init__()
        self.exceptions = exceptions
        self.cause = cause


class BalladRollback(Exception):
    """
    Some code has asked for the entire ballad to be rolled back. cause
    of the BalladException will be None if something goes wrong during
    rollback, and this exception will be suppressed on exit from the
    ballad (context manager) if not.
    """

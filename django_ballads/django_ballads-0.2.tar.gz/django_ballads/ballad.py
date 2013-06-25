"""
Context manager that implements the main ballad mechanic.
"""

from django.db import transaction
from django_ballads.exceptions import BalladException, BalladRollback


# Different behaviour between Django 1.6 and previously.
# Newer is better; the older stuff is just so we can get work
# done until 1.6 is out.
if hasattr(transaction, 'atomic'):
    atomic = transaction.atomic
else:
    atomic = transaction.commit_on_success


class Ballad(object):
    """
    Context manager for managing rollbacks of multiple different
    systems. Automatically wraps in a database transaction (using
    transaction.commit_on_success or, if available,
    transaction.atomic) for a single chosen database connection.
    """
    # It would be nice to wrap multiple transaction.atomics, for
    # different databases. The API for that might prove fiddly
    # however, so I'm punting on this for now. (In most situations
    # you can just put another transaction.atomic with block inside,
    # although if something goes wrong in *its* rollback recovery
    # the final exceptions won't be the same as if we supported it
    # directly. Alternatively, for individual DML statements, you can
    # use autocommit and provide an explicit compensating action.)

    def __init__(self, using=None, ignore_rollback_exceptions=False):
        self.atomic = atomic(using=using)
        self.compensations = []
        self.rolled_back = False
        self.ignore_rollback_exceptions = ignore_rollback_exceptions

    def __enter__(self):
        self.atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        exceptions = []
        try:
            if exc_type == BalladRollback:
                # Django < 1.6 keyed on exc_value, so ensure there is one
                self.atomic.__exit__(exc_type, True, traceback)
            else:
                self.atomic.__exit__(exc_type, exc_value, traceback)
        except Exception as e:
            exceptions.append(e)
        if exc_value is not None:
            # at this point the db will have rolled back
            # note that this means that the db & ORM are
            # accessible as normal, although no objects
            # constructed during the ballad will be saved
            # (they generally will exist in memory, however).
            for compensation in self.compensations:
                try:
                    compensation()
                except Exception as e:
                    exceptions.append(e)
            self.rolled_back = True

        if len(exceptions) > 0 and not self.ignore_rollback_exceptions:
            # wrap them up in a BalladException, including the
            # exception that got us here if it wasn't a BalladRollback.
            if exc_type == BalladRollback:
                raise BalladException(exceptions)
            else:
                raise BalladException(exceptions, (exc_type, exc_value, traceback))
        elif exc_type==BalladRollback:
            # suppress
            return True

    def stanza(self):
        """
        Return a context manager which you can set a compensation on
        that will be added to the ballad.
        """

        class Stanza(object):
            """
            Context manager for adding a single compensation
            to its parent ballad. Useful if you need to
            adjust a compensation due to later actions, but
            don't want to use an object for the compensation.
            """
            def __init__(self, ballad):
                self.ballad = ballad
                self.compensation = None

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                if self.compensation is not None:
                    self.ballad.compensation(self.compensation)

        return Stanza(self)

    def rollback(self):
        """
        Rollback the ballad, performing all compensating actions and
        rolling back the implicit database transaction. You can also
        just raise BalladRollback, although this is probably clearer.
        """
        raise BalladRollback()

    def compensation(self, action):
        """
        Add a compensating action for some work you've done in the ballad.
        """
        self.compensations.append(action)

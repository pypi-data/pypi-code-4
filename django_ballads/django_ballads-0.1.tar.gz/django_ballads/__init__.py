"""
Django transactional ballads -- composing database transactions
with non-database operations.

    from django_ballad import Ballad
    
    with Ballad(using='default') as ballad:
        orm_obj1 = db_operations()

        file_obj = make_file_part(orm_obj1)
        ballad.compensation(lambda: file_obj.unlink())

        remote_obj = call_remote_api(orm_obj1, file_obj)
        ballad.compensation(lambda: remote_obj.delete())

        orm_obj2 = more_db_operations()

Call .rollback() to rollback everything done up to now and exit the
with block without an exception, or any other exception will rollback
and re-raise.

    with Ballad() as ballad:
        charge = call_remote_charge_api()
        ballad.compensation(lambda: charge.refund())

        updated = Order.objects.filter(id=order_id).update(paid=True)
        if updated != 1:
            ballad.rollback()

If exceptions occur *during* rollback (including during the db
rollback that happens automatically in the nested database
transaction), then a BalladException will be raised containing those
exceptions. Its cause attribute will give the original exception that
caused the rollback, unless it was an explicit BalladRollback.

The BalladException behaviour can be suppressed by passing
ignore_rollback_exceptions=True to the Ballad constructor, in which
case it will act as if nothing went wrong during rollback.

No matter what, all rollback compensating actions will be run even if
earlier ones fail. This should be considered when writing compensating
actions.
"""

from django_ballads.exceptions import BalladException, BalladRollback
from django_ballads.ballad import Ballad

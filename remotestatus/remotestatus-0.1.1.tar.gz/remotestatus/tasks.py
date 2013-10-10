from celery.decorators import periodic_task
from celery.task.schedules import crontab

from django.conf import settings
from django.utils.timezone import now

from remotestatus.conf import REMOTE_CHECK_FREQUENCY
from remotestatus.models import CallRound
from remotestatus.remote import remote_manager


@periodic_task(run_every=crontab(minute="*/%d" % REMOTE_CHECK_FREQUENCY))
def monitor_remote_status():
    """
    Iterate over each RemoteBox in the registry and:
        1. Check its status and the status of its optional procs.
        2. Save the status of each in the data store.
    """
    # Incr the `call_round` for this 'round' of remote calls
    call_round = CallRound.objects.create(date_checked=now())

    # Collect the downed boxes/processes and eventually alert admins
    unreachable_remotes = []
    invalid_procs = []

    for remote_box in remote_manager.registry.values():
        # Get status of the box
        status = remote_box.check_remote_status()

        if not remote_box.is_reachable(status):
            unreachable_remotes.append(remote_box)
        elif not remote_box.has_valid_procs(status):
            invalid_procs.append(remote_box)

        # Update the datastore with the status of the box
        remote_box.save_status_history(call_round, status)

    # Send a rollup notification to the admin about all unreachable remote boxes
    print 'UNREACHABLE REMOTES: %d' % len(unreachable_remotes)
    print 'INVALID PROCS: %d' % len(invalid_procs)
    remote_manager.notify_admin(unreachable_remotes, invalid_procs)

from celery.task.schedules import crontab
from celery.task import periodic_task
from django.core import management


@periodic_task(run_every=crontab(minute=0, hour=4))
def clear_caches():
    """
    Clear stale cache sessions in db at 4am every day
    """
    management.call_command('clearsessions', verbosity=0, interactive=False)

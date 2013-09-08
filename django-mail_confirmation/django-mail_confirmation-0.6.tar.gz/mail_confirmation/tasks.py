from celery.task.schedules import crontab
from celery.task import periodic_task

from .utils import clear_stale as clear_stale_confirmations


@periodic_task(run_every=crontab(day_of_week='1',hour='12'))
def clear_stale():
    """
    Clear stale confirmations every monday at 12pm 
    """
    clear_stale_confirmations()

from django.core.management import call_command

from celery import task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@task(max_retries=3)
def syncldap():
    """
    Call the appropriate management command to synchronize the LDAP users
    with the local database.
    """
    try:
        call_command('syncldap')
    except Exception as exc:
        logger.warn("Synchronize LDAP task failed, retrying")
        raise syncldap.retry(exc=exc, countdown=60)

# Hook BatchSessionCleanupCommand up to django-admin
# See https://docs.djangoproject.com/en/1.3/howto/custom-management-commands/

from batch_session_cleanup.commands import BatchSessionCleanupCommand as Command

from templated_email.backends.database.models import EmailTemplate
from django.db.models.signals import post_syncdb
from django.conf import settings


def sync_emailtemplate(sender, **kwargs):
    if sender.__name__ == 'templated_email.backends.database.models':
        defaults = getattr(settings, 'TEMPLATED_EMAIL_DEFAULTS', None)
        if defaults:
            for params in defaults:
                EmailTemplate.objects.create(**params)


post_syncdb.connect(sync_emailtemplate)

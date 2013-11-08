import os


VERSION = '0.1.3'


if 'DJANGO_SETTINGS_MODULE' in os.environ:
    from django.utils.translation import ugettext as _

    # custom language strings
    _('Django_Queue_Mailer')
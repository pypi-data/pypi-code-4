from django.conf import settings

SUPPORT_EMAIL = getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL)
SUPPORT_EMAIL_SUBJECT = getattr(settings, 'SUPPORT_EMAIL_SUBJECT', 'Support Message')
SUPPORT_WAIT_SEND = getattr(settings, 'SUPPORT_WAIT_SEND', True)

from django.conf import settings
from django_diazo import defaults


def get_setting(setting, override=None):
    if override is not None:
        return override
    if hasattr(settings, 'DIAZO_{0}'.format(setting)):
        return getattr(settings, 'DIAZO_{0}'.format(setting))
    else:
        return getattr(defaults, setting)

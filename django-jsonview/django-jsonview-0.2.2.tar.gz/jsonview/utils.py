import json
from django.conf import settings


def get_setting(setting, default=None, memo={}):
    if setting not in memo:
        memo[setting] = getattr(settings, setting, default)
    return memo[setting]


def dump_json(obj, cls=None):
    if cls is None and get_setting('JSONVIEW_ENCODER') is not None:
        pass

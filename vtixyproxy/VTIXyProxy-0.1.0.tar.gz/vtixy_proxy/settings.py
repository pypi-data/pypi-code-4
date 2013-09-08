from django.conf import settings
from rest_framework.settings import APISettings
from rest_framework_proxy.settings import DEFAULTS

REST_PROXY = {
    'HOST': getattr(settings, 'VTIXY_HOST', None),
    'AUTH': {
        'user': getattr(settings, 'VTIXY_LOGIN', None),
        'password': getattr(settings, 'VTIXY_PASSWORD', None),
    },
}

vtixy_uat_proxy_settings = APISettings(REST_PROXY, DEFAULTS)
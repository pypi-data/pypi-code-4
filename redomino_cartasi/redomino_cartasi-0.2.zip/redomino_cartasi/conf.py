from django.conf import settings

MAC_KEY = settings.MAC_KEY_CARTASI
TERMINAL_ID = settings.TERMINAL_ID_CARTASI
ACTION_CODE = settings.ACTION_CODE_CARTASI
CURRENCY = settings.CURRENCY_CARTASI
LANGUAGE = settings.LANGUAGE_CARTASI
NOTIFICATION_URL = getattr(settings, 'NOTIFICATION_URL_CARTASI', 'cartasi/paid_cartasi')
RESULT_URL = getattr(settings, 'RESULT_URL_CARTASI', 'cartasi/thank-you')
ERROR_URL = getattr(settings, 'ERROR_URL_CARTASI', 'cartasi/error')
ANNULMENT_URL = getattr(settings, 'ANNULMENT_URL_CARTASI', 'cartasi/annulment')
VERSION_CODE = settings.VERSION_CODE_CARTASI
MESSAGE_TYPE = settings.MESSAGE_TYPE_CARTASI
CO_PLATFORM = settings.CO_PLATFORM_CARTASI
VPOS_ACTION = settings.VPOS_ACTION_CARTASI


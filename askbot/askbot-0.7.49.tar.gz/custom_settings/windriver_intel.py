#ASKBOT_EXTRA_SKINS_DIR = '/Users/evgenyfadeev/windriver-theme'
import site
site.addsitedir('/Users/evgenyfadeev/askbot-extensions/windriver-app/')
from settings import *

SERVER_EMAIL = 'server@example.com'

INSTALLED_APPS += ('windriver',)
TEMPLATE_CONTEXT_PROCESSORS += (
    'windriver.context.windriver_context',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'vivisimo': {
            '()': 'windriver.logging_filters.VivisimoFilter',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['vivisimo'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
            'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

REPORTS_SUBJECT_LINE = 'aha reports subject link'
REPORTS_RECIPIENTS = ('recipient1@example.com',)

COMPANY_GROUP_NAME = 'everyone'#Wind River'

COUNTRY_CODES = {
    'ja': 'jp',
    'en': 'us'
}

ASKBOT_SITE_IDS = [1, 2]
ASKBOT_TAG_ISOLATION = 'per-site'
SESSION_COOKIE_DOMAIN = '.askbot.com'

INTEL_KF_URL = 'http://intel.askbot.com:8001'
INTEL_KF_NAME = 'IDT Toolkit for Data Gateways Knowledge Forum'
INTEL_DOCS_URL = 'http://intel-docs.askbot.com:8002'
INTEL_DOCS_NAME = 'Documents &amp; Downloads'
WINDRIVER_KF_URL = 'http://windriver.askbot.com:8000'
WINDRIVER_KF_NAME = 'Wind River Knowledge Forum'

UZE_TZ = False

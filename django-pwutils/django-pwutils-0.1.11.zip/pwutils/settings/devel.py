
import os

from .base import *

DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DUMMY = True

# remove cached loader from template loaders
try:
    if 'cached.Loader' in TEMPLATE_LOADERS[0][0]:
        TEMPLATE_LOADERS = TEMPLATE_LOADERS[0][1]
except IndexError:
    pass

INSTALLED_APPS = INSTALLED_APPS + (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PROJECT_ROOT, 'messages')

DEBUG_TOOLBAR_PANELS = (
  'debug_toolbar.panels.version.VersionDebugPanel',
  'debug_toolbar.panels.timer.TimerDebugPanel',
  'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
  'debug_toolbar.panels.headers.HeaderDebugPanel',
  'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
  'debug_toolbar.panels.template.TemplateDebugPanel',
  'debug_toolbar.panels.sql.SQLDebugPanel',
  'debug_toolbar.panels.signals.SignalDebugPanel',
  'debug_toolbar.panels.logger.LoggingPanel',
  'debug_toolbar.panels.cache.CacheDebugPanel',
  #debug_toolbar.panels.profiling.ProfilingDebugPanel',
)

DEBUG_TOOLBAR_CONFIG = {
#    'ENABLE_STACKTRACES': True,
    'INTERCEPT_REDIRECTS': False,
}

# For sql_queries
INTERNAL_IPS = (
    "127.0.0.1",
)


LOGGING = {
  'version': 1,
  'handlers': {
    'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },

  },
  'loggers': {
    '': {
      'handlers': ['console'],
      'level': 'DEBUG',
    },
    'django': {
      'handlers': ['console'],
      'level': 'INFO',
    }

  }
}

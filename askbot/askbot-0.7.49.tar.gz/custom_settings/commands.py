import site
import os.path

COMMANDS_COM_REPO_DIR = '/Users/evgenyfadeev/clients/dtannen/commands-app'
site.addsitedir(COMMANDS_COM_REPO_DIR)
site.addsitedir('/Users/evgenyfadeev/askbot-main/env/lib/python2.7/site-packages')

from settings import *

ASKBOT_SERVICE_URL_PREFIX = 'ab/'

ENVIRONMENT = 'loc:8000'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

ASKBOT_EXTRA_SKINS_DIR = os.path.join(COMMANDS_COM_REPO_DIR, 'askbot_themes')

THEME_MEDIA_PATH = 'askbot_theme/media/commands'
STATICFILES_DIRS += (
    ('css', os.path.join(COMMANDS_COM_REPO_DIR, 'static', 'css')),
    ('js', os.path.join(COMMANDS_COM_REPO_DIR, 'static', 'js')),
    ('img', os.path.join(COMMANDS_COM_REPO_DIR, 'static', 'img')),
)

LIVESETTINGS_OPTIONS = {
    1: {
        'DB': True,
        'SETTINGS': {
            'GENERAL_SKIN_SETTINGS': {
                'ASKBOT_DEFAULT_SKIN': 'askbot_theme',
            },
            'FORUM_DATA_RULES': {
                'SPACES_ENABLED': True
            }
        }
    }
}

INSTALLED_APPS += (
    'website',
    'feedback'
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'website.context.commands_com_context',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.sqlprint.SqlPrintingMiddleware',
    'commands_com.middleware.SubdomainMiddleware',

    #below is askbot stuff for this tuple
    'askbot.middleware.anon_user.ConnectToSessionMessagesMiddleware',
    'askbot.middleware.forum_mode.ForumModeMiddleware',
    'askbot.middleware.cancel.CancelActionMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'askbot.middleware.view_log.ViewLogMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'askbot.middleware.spaceless.SpacelessMiddleware',
    'custom_settings.middleware.P3PHeadersMiddleware'
)

ROOT_URLCONF = 'commands_com.urls'

FEEDBACK_CHOICES = [('bug', 'Bug'), ('feature_request', 'Feature Request')]
RECAPTCHA_PUBLIC_KEY = '6LchP-ASAAAAAMo23U6-P1wMe-z6zbNWOD1NAuTK'
RECAPTCHA_PRIVATE_KEY = '6LchP-ASAAAAANlLUXCeVsP3f-MKOlBlpvOjoxiv'

ASKBOT_QUESTIONS_PAGE_EXTRA_CONTEXT = 'website.views.get_command_page_context'

_ = lambda v:v #fake translation function for the login url
LOGIN_URL_PATH = '/%s%s%s' % (ASKBOT_URL,_('account/'),_('signin/'))
LOGIN_URL = 'http://commands.' + ENVIRONMENT + LOGIN_URL_PATH

SESSION_COOKIE_DOMAIN = '.commands.loc'
ORDERED_PLATFORM_NAMES = [
    'Linux', 'Windows', 'Mac',
    'Shell', 'Vi', 'Git', 'SVN',
    'FTP', 'DOS',
]

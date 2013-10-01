
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

SITE_NAME = 'test'
SITE_ID = 1
SERVICE_NAME = 'swingers'

ROOT_URLCONF = 'urls'

USE_TZ = True

MIDDLEWARE_CLASSES = (
    'swingers.middleware.html.HtmlMinifyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'swingers.middleware.transaction.TransactionMiddleware',
    'swingers.middleware.auth.AuthenticationMiddleware',
)

ALLOW_ANONYMOUS_ACCESS = False
ANONYMOUS_USER_ID = -1

INSTALLED_APPS = (
    'swingers',
    'swingers.sauth',
    'swingers.tests',   # the test fixtures are loaded from here

    'reversion',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    'django.contrib.messages',
    'django.contrib.gis',
)

SECRET_KEY = 'test'

STATIC_URL = '/static/'

HTML_MINIFY = True

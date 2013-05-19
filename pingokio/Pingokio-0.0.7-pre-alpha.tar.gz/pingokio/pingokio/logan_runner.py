#-*- coding:utf8 -*-
import os
import base64
from logan.runner import run_app

KEY_LENGTH = 40

CONFIG_TEMPLATE = """
import os.path

CONF_ROOT = os.path.dirname(__file__)

DATABASES = {
'default': {
# You can swap out the engine for MySQL easily by changing this value
# to ``django.db.backends.mysql`` or to PostgreSQL with
# ``django.db.backends.postgresql_psycopg2``

# If you change this, you'll also need to install the appropriate python
# package: psycopg2 (Postgres) or mysql-python
'ENGINE': 'django.db.backends.sqlite3',

'NAME': os.path.join(CONF_ROOT, 'sentry.db'),
'USER': 'postgres',
'PASSWORD': '',
'HOST': '',
'PORT': '',

# If you're using Postgres, we recommend turning on autocommit
# 'OPTIONS': {
# 'autocommit': True,
# }
}
}

# If you're expecting any kind of real traffic on Sentry, we highly recommend configuring
# the CACHES and Redis settings

# You'll need to install the required dependencies for Memcached:
# pip install python-memcached
#
# CACHES = {
# 'default': {
# 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
# 'LOCATION': ['127.0.0.1:11211'],
# }
# }

###########
## Queue ##
###########

# See http://sentry.readthedocs.org/en/latest/queue/index.html for more
# information on configuring your queue broker and workers.

# You can enable queueing of jobs by turning off the always eager setting:
# CELERY_ALWAYS_EAGER = False
# BROKER_URL = 'redis://localhost:6379'

####################
## Update Buffers ##
####################

# Buffers (combined with queueing) act as an intermediate layer between the database and
# the storage API. They will greatly improve efficiency on large numbers of the same events
# being sent to the API in a short amount of time.

# You'll need to install the required dependencies for Redis buffers:
# pip install redis hiredis nydus
#
# SENTRY_BUFFER = 'sentry.buffer.redis.RedisBuffer'
# SENTRY_REDIS_OPTIONS = {
# 'hosts': {
# 0: {
# 'host': '127.0.0.1',
# 'port': 6379,
# }
# }
# }

SENTRY_KEY = %(default_key)r

# You MUST configure the absolute URI root for Sentry:
SENTRY_URL_PREFIX = 'http://sentry.example.com' # No trailing slash!

SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 9000
SENTRY_WEB_OPTIONS = {
'workers': 3, # the number of gunicorn workers
'secure_scheme_headers': {'X-FORWARDED-PROTO': 'https'},
}

# Mail server configuration

# For more information check Django's documentation:
# https://docs.djangoproject.com/en/1.3/topics/email/?from=olddocs#e-mail-backends

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False

# http://twitter.com/apps/new
# It's important that input a callback URL, even if its useless. We have no idea why, consult Twitter.
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

# http://developers.facebook.com/setup/
FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''

# http://code.google.com/apis/accounts/docs/OAuth2.html#Registering
GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''

# https://github.com/settings/applications/new
GITHUB_APP_ID = ''
GITHUB_API_SECRET = ''

# https://trello.com/1/appKey/generate
TRELLO_API_KEY = ''
TRELLO_API_SECRET = ''
"""


def generate_settings():
    """
    This command is run when ``default_path`` doesn't exist, or ``init`` is
    run and returns a string representing the default data to put into their
    settings file.
    """
    output = CONFIG_TEMPLATE % dict(
        default_key=base64.b64encode(os.urandom(KEY_LENGTH)),
    )

    return output


def main():
    run_app(
        project='pingokio',
        default_config_path='~/.pingokio/',
        default_settings='pingokio.settings',
        settings_initializer='pingokio.logan_runner.generate_settings',
        settings_envvar='PINGOKIO_CONF',
    )

if __name__ == '__main__':
    main()

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

'NAME': os.path.join(CONF_ROOT, 'pingokio.db'),
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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False
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
        default_config_path='~/.pingokio/pingokio_settings.py',
        default_settings='pingokio.server.settings',
        settings_initializer=generate_settings,
        settings_envvar='PINGOKIO_CONF',
    )

if __name__ == '__main__':
    main()

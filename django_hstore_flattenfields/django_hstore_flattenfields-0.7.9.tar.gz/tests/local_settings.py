# encoding: utf-8
import os

DBNAME = 'zambedb'
DBUSER = 'zambe'
DBPASS = '1q2w3e'
if os.environ.has_key('PG_USER'):
    DBUSER = os.environ['PG_USER']
    DBPASS = os.environ['PG_PASSWORD']
    DBNAME = 'postgres'

DATABASES = {
    'default': {
        'ENGINE': 'django_hstore.postgresql_psycopg2',
        'NAME': DBNAME,
        'USER': DBUSER,
        'PASSWORD': DBPASS,
        'HOST': '',
        'PORT': '5432',
    }
}

# The version of your postgres db, must be >= 9.1.
PG_VERSION = (9.1,)

HSTORE_DYNAMIC_MODEL = 'app.DynamicField'

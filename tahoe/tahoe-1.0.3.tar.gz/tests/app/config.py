import os


class Testing(object):
    DEBUG = True
    TESTING = True

    SECURITY_PASSWORD_HASH = 'plaintext'
    SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlite:///testing.db'
    # Forces Celery to execute tasks immediately while blocking
    CELERY_ALWAYS_EAGER = True

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SESSION_PROTECTION = False

    SECURITY_RESET_SALT = 'TESTING_SALT'
    SECURITY_PASSWORD_SALT = 'TESTING_SALT'
    SECRET_KEY = 'TESTING_KEY'
    SESSION_SALT = 'TESTING_SALT'

    MAIL_SERVER = 'mail.tahoe.local'
    MAIL_PORT = 587
    MAIL_DEBUG = True

    MAIL_USERNAME = 'test'
    MAIL_PASSWORD = 'test'

    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_SUPPRESS_SEND = True
    MAIL_FAIL_SILENTLY = False
    DEFAULT_MAIL_SENDER = 'Tahoe <noreply@tahoe.local>'

    SECURITY_BLUEPRINT_NAME = ''

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_ACCESS_KEY_SECRET = os.environ.get('AWS_ACCESS_KEY_SECRET')

    ELASTIC_SEARCH_SERVERS = ['127.0.0.1:9200']
    MEMCACHED_SERVERS = ['127.0.0.1:11211']

    # For Task Workers
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600
    }
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ENABLE_UTC = True

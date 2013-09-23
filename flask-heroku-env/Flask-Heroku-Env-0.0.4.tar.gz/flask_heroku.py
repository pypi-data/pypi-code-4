#!/user/bin/env python

from os import environ


class Heroku(object):
    """Heroku configurations for flask."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # sqlalchemy
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', environ.get('DATABASE_URL'))

        # mailgun
        if 'MAILGUN_SMTP_SERVER' in environ:
            app.config.setdefault('SMTP_SERVER', environ.get('MAILGUN_SMTP_SERVER'))
            app.config.setdefault('SMTP_LOGIN', environ.get('MAILGUN_SMTP_LOGIN'))
            app.config.setdefault('SMTP_PASSWORD', environ.get('MAILGUN_SMTP_PASSWORD'))
            app.config.setdefault('MAIL_SERVER', environ.get('MAILGUN_SMTP_SERVER'))
            app.config.setdefault('MAIL_USERNAME', environ.get('MAILGUN_SMTP_LOGIN'))
            app.config.setdefault('MAIL_PASSWORD', environ.get('MAILGUN_SMTP_PASSWORD'))
            app.config.setdefault('MAIL_USE_TLS', True)

        # memcachier
        app.config.setdefault('CACHE_MEMCACHED_SERVERS', environ.get('MEMCACHIER_SERVERS'))
        app.config.setdefault('CACHE_MEMCACHED_USERNAME', environ.get('MEMCACHIER_USERNAME'))
        app.config.setdefault('CACHE_MEMCACHED_PASSWORD', environ.get('MEMCACHIER_PASSWORD'))

        # rediscloud
        app.config.setdefault('BROKER_URL', environ.get('REDISCLOUD_URL'))
        app.config.setdefault('BROKER_BACKEND', environ.get('REDISCLOUD_URL'))

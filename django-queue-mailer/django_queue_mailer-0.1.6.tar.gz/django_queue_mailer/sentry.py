from django.conf import settings


raven_config = getattr(settings, 'RAVEN_CONFIG', None)


def get_raven():
    # not properly configured
    try:
        dsn = raven_config['dsn']
    except Exception:
        return None

    try:
        from raven import Client
        client = Client(dsn)
        return client

    except ImportError:
        return None

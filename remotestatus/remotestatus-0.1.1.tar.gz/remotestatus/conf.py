from django.conf import settings


# Frequency with which checks will be made to the remote boxes (default is 10 min.)
REMOTE_CHECK_FREQUENCY = getattr(settings, 'RS_REMOTE_CHECK_FREQUENCY', 10 * 60 * 60)
DEFAULT_KEY_FILE = getattr(settings, 'RS_KEY_FILE', None)
DEFAULT_KNOWN_HOSTS_FILE = getattr(settings, 'RS_KNOWN_HOSTS_FILE', None)
DEFAULT_PROXY_HOSTNAME = getattr(settings, 'RS_PROXY_HOSTNAME', None)
DEFAULT_PROXY_USERNAME = getattr(settings, 'RS_PROXY_USERNAME', None)
DEFAULT_PROXY_PORT = getattr(settings, 'RS_PROXY_PORT', None)
USERS_TO_NOTIFY = getattr(settings, 'RS_USERS_TO_NOTIFY', [])
NOTIFICATION_EMAIL_ADDRESS = getattr(settings, 'RS_NOTIFICATION_EMAIL_ADDRESS', 'notifier@remotestatus.com')
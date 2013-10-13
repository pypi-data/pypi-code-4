from django.contrib.auth.middleware import RemoteUserMiddleware

class DjangoNginxRemoteUserMiddleware(RemoteUserMiddleware):
    header = 'HTTP_REMOTE_USER'
from django.contrib.auth.middleware import RemoteUserMiddleware


class CustomHeaderMiddleware(RemoteUserMiddleware):
    """
    Authentication is done by httpd server and certificate DN is passed as a username to web application.
    """
    header = 'SSL_CLIENT_S_DN'

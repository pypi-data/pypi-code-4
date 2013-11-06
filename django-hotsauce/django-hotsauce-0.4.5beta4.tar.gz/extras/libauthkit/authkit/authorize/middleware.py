#
# Authorize Objects
#

__all__ = ['middleware']


class _Authorize(object):
    def __init__(self, app, permission):
        self.app = app
        self.permission = permission

    def __call__(self, environ, start_response):
        all_conf = environ.get('authkit.config')
        if all_conf is None:
            raise Exception('Authentication middleware not present')
        if all_conf.get('setup.enable', True) is True:
            # Could also check that status and response haven't changed here?
            try:
                return self.permission.check(self.app, environ, start_response)
            except NotAuthenticatedError:
                if environ.has_key('REMOTE_USER'):
                    raise NonConformingPermissionError(
                        'Faulty permission: NotAuthenticatedError raised '
                        'but REMOTE_USER key is present.'
                    )
                else:
                    raise
        else:
            return self.app(environ, start_response)

def middleware(app, permission):
    """
    Returns an WSGI app wrapped in authorization middleware and on each request
    will check the permission specified.

    Takes the arguments:

    ``app``
        The WSGI application to be wrapped

    ``permission``
        The AuthKit permission object to be checked.

    The ``httpexceptions`` and ``authkit.authenticate.middleware`` middleware need to
    be wrap this middleware otherwise any errors triggered will not be intercepted.

    See the AuthKit manual for an example.
    """
    return _Authorize(app, permission)



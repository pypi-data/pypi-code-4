#!/usr/bin/env python

__all__ = ['PermissionError', 'NotAuthenticatedError', 
    'NotAuthorizedError', 'NonConformingPermissionError']


class PermissionError(BaseException):
    """
    Base class from which ``NotAuthenticatedError`` and ``NotAuthorizedError`` 
    are inherited.
    """
    pass

class NotAuthenticatedError(PermissionError):
    """
    Raised when a permission check fails because the user is not authenticated.

    The exception is caught by the ``httpexceptions`` middleware and converted into
    a ``401`` HTTP response which is intercepted by the authentication middleware
    triggering a sign in.
    """
    required_headers = ()
    code = 401
    title = 'Not Authenticated'

class NotAuthorizedError(NotAuthenticatedError):
    """
    Raised when a permission check fails because the user is not authorized.

    The exception is caught by the ``httpexceptions`` middleware and converted into
    a ``403`` HTTP response which is intercepted by the authentication middleware
    triggering a sign in.
    """
    code = 403
    title = 'Forbidden'
    explanation = ('Access was denied to this resource.')


class NonConformingPermissionError(NotAuthorizedError):
    """
    Raised when a custom permission object is not behaving in a compliant way
    """
    pass


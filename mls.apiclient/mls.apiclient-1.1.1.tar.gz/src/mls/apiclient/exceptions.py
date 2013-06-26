# -*- coding: utf-8 -*-
"""mls.apiclient exception classes."""


class MLSError(Exception):
    """Main exception class."""
    pass


class ImproperlyConfigured(MLSError):
    """This exception is raised on configuration errors."""
    pass


class ObjectNotFound(MLSError):
    """This exception is raised if an object can not be found."""
    pass


class MultipleResults(MLSError):
    """This exception is raised on multiple results.

    That is, if a get request returns more than one result.
    """
    def __str__(self):
        return 'Your query had multiple results.'

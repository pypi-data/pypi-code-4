#coding:utf-8
class BackendUnavailable(Exception):
    """
    Raised when a Backend is not available
    """
    pass


class InvalidKey(Exception):
    """
    Raised when a key is invalid for the Backend.
    """

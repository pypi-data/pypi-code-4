"""
exceptions.py

Contains exception classes for CNSdi

ServiceNotFound is used by di.ServiceStore

All CNSdi exceptions require a message passed into the constructor.
"""

class BaseDIException(Exception):
    """Base exception class for CNSdi"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ServiceNotFound(BaseDIException):
    """Used when a service cannot be found"""
    pass
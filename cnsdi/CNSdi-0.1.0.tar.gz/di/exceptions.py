__author__ = 'sscoble'

class BaseDIException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ServiceNotFound(BaseDIException): pass
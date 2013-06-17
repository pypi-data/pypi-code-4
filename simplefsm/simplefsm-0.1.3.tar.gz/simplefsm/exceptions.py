'''SimpleFSM Exceptions'''


class InvalidStateError(Exception):
    '''A change to an invalid state was attempted'''
    def __init__(self, message, errors=None):
        super(InvalidStateError, self).__init__(message)
        self.message = message
        self.errors = errors


class MethodNotAllowedError(Exception):
    '''The method call attempted is not permitted'''
    def __init__(self, message, errors=None):
        super(MethodNotAllowedError, self).__init__(message)
        self.message = message
        self.errors = errors


class InconsistentModelError(Exception):
    '''The state model is not self-consistent'''
    def __init__(self, message, errors=None):
        super(InconsistentModelError, self).__init__(message)
        self.message = message
        self.errors = errors

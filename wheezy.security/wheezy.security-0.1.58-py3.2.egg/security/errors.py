
""" ``errors`` module.
"""


class SecurityError(RuntimeError):
    """ Raised when a security error occurs. It is subclass of
        ``RuntimeError``.
    """

    def __init__(self, message):
        self.message = message

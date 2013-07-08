""" :mod:`hedwig.backends`
    ~~~~~~~~~~~~~~~~~~~~~~

"""
from .base import BaseEmailBackend
from .console import ConsoleEmailBackend
from .smtp import SMTPEmailBackend

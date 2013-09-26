# -*- coding: utf-8 -*-

# Requests Futures

"""
async requests HTTP library
~~~~~~~~~~~~~~~~~~~~~


"""

__title__ = 'requests-futures'
__version__ = '0.9.0'
__build__ = 0x000000
__author__ = 'Pierre Tardy'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Pierre Tardy'

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
try:
	from .sessions import Session
except ImportError:
	Session = None
__exports__ = [Session]

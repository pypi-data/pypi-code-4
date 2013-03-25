# -*- coding: utf-8 -*-

#   __
#  /__)  _  _     _   _ _/   _
# / (   (- (/ (/ (- _)  /  _)
#          /

"""
requesocks
~~~~~~~~

:copyright: (c) 2012 by Kenneth Reitz.
:license: ISC, see LICENSE for more details.

"""

__title__ = 'requesocks'
__version__ = '0.10.8'
__build__ = 0x001008
__author__ = 'Kenneth Reitz'
__license__ = 'ISC'
__copyright__ = 'Copyright 2012 Kenneth Reitz'


from . import utils
from .models import Request, Response
from .api import request, get, head, post, patch, put, delete, options
from .sessions import session, Session
from .status_codes import codes
from .exceptions import (
    RequestException, Timeout, URLRequired,
    TooManyRedirects, HTTPError, ConnectionError
)

#!/usr/bin/env python
# coding=utf-8

"""cloudns api python client.

The cloudns API is documented at http://wiki.dev.game.yy.com/moin/DNS

This python client is based on that API.

The major version of this client tries to match the the API version. Thus from
1.1.0, it will support API v1.1.

"""

__version__ = '1.1.0.1'
__maintainer__ = 'g-yygame-brd@yy.com'


from base import (logger, CloudnsError, CloudnsRuntimeError,
                  CloudnsServerError,
                  CloudnsValidationError, CloudnsBadUsage, RecordNotFound,
                  DuplicateRecord, RecordNotReady,
                  PENDING_ACTIVE, ACTIVE, PENDING_REMOVAL)
from record import Record
from user import User
from zone import Zone

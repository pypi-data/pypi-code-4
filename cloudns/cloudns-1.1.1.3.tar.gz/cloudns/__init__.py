#!/usr/bin/env python
# coding=utf-8

"""cloudns API python client.

The cloudns API is documented at http://wiki.dev.game.yy.com/moin/DNS

This python client is based on that API.

The major version of this client tries to match the the API version. Thus
1.1.* (or later) supports API v1.1.

"""

# about versioning, the pattern is a.b.x.y.
# a.b will always match the upstream cloudns API. x.y is controlled here.
# increment x when a major feature is added,
# increment y for a bug fix or a minor document update etc.
__version__ = '1.1.1.3'
__maintainer__ = 'g-yygame-brd@yy.com'


from .base import (logger, CloudnsError, CloudnsRuntimeError,
                   CloudnsServerError,
                   CloudnsValidationError, CloudnsBadUsage, RecordNotFound,
                   DuplicateRecord, RecordNotReady,
                   PENDING_ACTIVE, ACTIVE, PENDING_REMOVAL)
from .record import Record
from .user import User
from .zone import Zone

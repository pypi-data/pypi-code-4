#!/usr/bin/env python
# coding=utf-8

"""
defines exception types and constants
"""

import logging
logging.basicConfig(format='%(levelname)-8s %(message)s',
                    level=logging.INFO)
logger = logging.getLogger('cloudns')

_t1 = logging.getLogger('requests')
_t1.setLevel(logging.WARNING)

# some defined zone and record status.

PENDING_ACTIVE = 0

ACTIVE = 1

PENDING_REMOVAL = 2


class CloudnsError(Exception):
    pass


class CloudnsRuntimeError(CloudnsError, RuntimeError):
    pass


class CloudnsValidationError(CloudnsError):
    pass


class CloudnsBadUsage(CloudnsError):
    pass


class CloudnsServerError(CloudnsRuntimeError):
    """an error occurred on cloudns server, not your fault.

    """
    pass


class RecordNotFound(CloudnsRuntimeError):
    pass


class DuplicateRecord(CloudnsRuntimeError):
    """raised when you want to create a duplicate record.

    two records are dup if zone, name, content, isp are all the same.

    """
    pass


class RecordNotReady(CloudnsRuntimeError):
    """raised when you delete a record that is in PENDING_ACTIVE status.

    """
    pass

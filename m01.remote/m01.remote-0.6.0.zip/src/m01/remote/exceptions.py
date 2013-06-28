###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Exceptions
$Id:$
"""
__docformat__ = "reStructuredText"

import sys
import traceback
from zope.exceptions.exceptionformatter import format_exception


def getTraceback(as_html=True):
    """Returns a formatted traceback string"""
    t, v, b = sys.exc_info()
    try:
        return u''.join(format_exception(t, v, b, as_html=as_html))
    finally:
        del b


class RemoteException(Exception):
    """An error occurred while executing the job, abort now."""
    pass

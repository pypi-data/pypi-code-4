##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: uclient.py 3783 2013-07-03 00:48:53Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import umemcache

import zope.interface

import p01.memcache.connector
import p01.memcache.client
from p01.memcache import interfaces


class UltraMemcacheClient(p01.memcache.client.MemcacheClient):
    """Same as MemcacheClient but based on umemcache"""

    zope.interface.implements(interfaces.IMemcacheClient)

    _memcacheClientFactory = umemcache.Client
    _connectorFactory = p01.memcache.connector.UltraConnector

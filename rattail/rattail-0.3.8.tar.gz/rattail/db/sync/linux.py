#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.db.sync.linux`` -- Database Synchronization for Linux
"""

import edbob
from edbob import db

from ...daemon import Daemon
from . import get_sync_engines, synchronize_changes


class SyncDaemon(Daemon):

    def run(self):
        remote_engines = get_sync_engines()
        if remote_engines:
            synchronize_changes(db.engine, remote_engines)


def get_daemon(pidfile=None):
    """
    Get a :class:`SyncDaemon` instance.
    """

    if pidfile is None:
        pidfile = edbob.config.get('rattail.db', 'sync.pid_path',
                                   default='/var/run/rattail/dbsync.pid')
    return SyncDaemon(pidfile)


def start_daemon(pidfile=None, daemonize=True):
    """
    Start the database synchronization daemon.
    """

    get_daemon(pidfile).start(daemonize)


def stop_daemon(pidfile=None):
    """
    Stop the database synchronization daemon.
    """

    get_daemon(pidfile).stop()

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
``rattail.win32.service`` -- Windows Service
"""


import logging

try:
    import win32serviceutil
except ImportError:
    # Mock out for Linux.
    class Object(object):
        pass
    win32serviceutil = Object()
    win32serviceutil.ServiceFramework = Object

import edbob


log = logging.getLogger(__name__)


class Service(win32serviceutil.ServiceFramework):
    """
    Base class for Windows service implementations.
    """

    def __init__(self, args):
        """
        Constructor.
        """

        import win32event

        win32serviceutil.ServiceFramework.__init__(self, args)

        # Create "wait stop" event, for main worker loop.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def Initialize(self):
        """
        Service initialization.
        """

        # Read configuration file(s).
        edbob.init('rattail', service=self._svc_name_)

        return True

    def SvcDoRun(self):
        """
        This method is invoked when the service starts.
        """

        import win32service
        import win32event
        import servicemanager
        from pywintypes import error
        from winerror import ERROR_LOG_FILE_FULL

        # Write start occurrence to Windows Event Log.
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ''))
        except error, e:
            if e.winerror == ERROR_LOG_FILE_FULL:
                log.error("SvcDoRun: Windows event log is full!")
            else:
                raise

        # Figure out what we're supposed to be doing.
        if self.Initialize():

            # Wait infinitely for stop request, while threads do their thing.
            log.info("SvcDoRun: All threads started; waiting for stop request.")
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            log.info("SvcDoRun: Stop request received.")

        else: # Nothing to be done...
            msg = "Nothing to do!  (Initialization failed.)"
            log.warning("SvcDoRun: {0}".format(msg))
            servicemanager.LogWarningMsg(msg)
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # Write stop occurrence to Windows Event Log.
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, ''))
        except error, e:
            if e.winerror == ERROR_LOG_FILE_FULL:
                log.error("SvcDoRun: Windows event log is full!")
            else:
                raise

    def SvcStop(self):
        """
        This method is invoked when the service is requested to stop itself.
        """

        import win32service
        import win32event

        # Let the SCM know we're trying to stop.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # Let worker loop know its job is done.
        win32event.SetEvent(self.hWaitStop)

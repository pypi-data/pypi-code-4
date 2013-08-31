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
``rattail.filemon.win32`` -- File Monitor for Windows
"""

import os.path
import Queue
import logging

from rattail import filemon
from rattail.win32.service import Service
from rattail.threads import Thread


name = __name__
if name == 'win32':
    name = 'rattail.filemon.win32'
log = logging.getLogger(name)


class RattailFileMonitor(Service):

    _svc_name_ = "RattailFileMonitor"
    _svc_display_name_ = "Rattail : File Monitoring Service"
    _svc_description_ = ("Monitors one or more folders for incoming files, "
                         "and performs configured actions as new files arrive.")

    def Initialize(self):
        """
        Service initialization.
        """

        if not Service.Initialize(self):
            return False

        # Read monitor profile(s) from config.
        self.monitored = filemon.get_monitor_profiles()

        # Make sure we have something to do.
        if not self.monitored:
            return False

        # Create monitor and action threads for each profile.
        for key, profile in self.monitored.iteritems():

            # Create a file queue for the profile.
            profile.queue = Queue.Queue()

            # Perform setup for each of the watched folders.
            for i, path in enumerate(profile.dirs, 1):

                # Maybe put all pre-existing files in the queue.
                if profile.process_existing:
                    filemon.queue_existing(profile, path)

                # Create a monitor thread for the folder.
                name = 'monitor_{0}-{1}'.format(key, i)
                log.debug("Initialize: starting '{0}' thread for folder: {1}".format(
                        name, path))
                thread = Thread(target=monitor_files,
                                name=name, args=(profile, path))
                thread.daemon = True
                thread.start()

            # Create an action thread for the profile.
            nam = 'actions_{0}'.format(key)
            log.debug("Initialize: starting '{0}' thread".format(name))
            thread = Thread(target=filemon.perform_actions,
                            name=name, args=(profile,))
            thread.daemon = True
            thread.start()

        return True
    

def monitor_files(profile, path):
    """
    Callable target for file monitor threads.
    """

    import win32file
    import win32con
    import winnt

    hDir = win32file.CreateFile(
        path,
        winnt.FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None)

    if hDir == win32file.INVALID_HANDLE_VALUE:
        log.warning("monitor_files: can't open directory with CreateFile(): {0}".format(path))
        return

    while True:
        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            False,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME)

        log.debug("monitor_files: ReadDirectoryChangesW() results: {0}".format(results))
        for action, fname in results:
            fpath = os.path.join(path, fname)
            if action in (winnt.FILE_ACTION_ADDED,
                          winnt.FILE_ACTION_RENAMED_NEW_NAME):
                log.debug("monitor_files: queueing '{0}' file: {1}".format(
                        profile.key, fpath))
                profile.queue.put(fpath)


if __name__ == '__main__':
    import win32serviceutil
    win32serviceutil.HandleCommandLine(RattailFileMonitor)

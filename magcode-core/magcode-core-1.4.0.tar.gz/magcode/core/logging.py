#
# Copyright (c) Net24 Limited, Christchurch, New Zealand 2011-2012
#       and     Voyager Internet Ltd, New Zealand, 2012-2013
#
#    This file is part of py-magcode-core.
#
#    Py-magcode-core is free software: you can redistribute it and/or modify
#    it under the terms of the GNU  General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Py-magcode-core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU  General Public License for more details.
#
#    You should have received a copy of the GNU  General Public License
#    along with py-magcode-core.  If not, see <http://www.gnu.org/licenses/>.
#
"""Logging and Debugging IO module

Provides daemon logging, and debug messaging support.

Uses the logging root logger. If debug_level is greater than 0, stderr
is added to the root logger as an additional handler.  Given that only
one process of the same name is allowed to run at a time on a machine,
logging to log files and syslog should also happen at the same time.
"""


import os
import sys
import syslog
import logging
import logging.handlers
try:
    import codecs
except ImportError:
    codecs = None

from magcode.core.globals_ import *
from magcode.core.utility import get_numeric_setting

log_object = None

class MagCodeSysLogHandler(logging.handlers.SysLogHandler):
    """Override broken SysLogHandler
    
    Messages in log end up with 3 bytes of cruft form misencoded priority
    integer.  This implementation uses libc functions to fix things
    """
    def __init__(self, address=None, 
            facility=syslog.LOG_USER, 
            socktype=None):
        """
        Open a logging session
        """
        logging.Handler.__init__(self)
        self.facility = facility
        syslog.openlog(process_name,
                syslog.LOG_PID|syslog.LOG_NDELAY, facility)
        self.formatter = None

    def close(self):
        """
        Closes logging session in libc
        """
        syslog.closelog()

    def emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the libc syslog function. If
        exception information is present, it is NOT sent to the server.
        """
        msg = self.format(record) + '\000'
        """
        We need to convert record level to lowercase, maybe this will
        change in the future.
        """
        syslog_priority = self.mapPriority(record.levelname)
        syslog_priority = self.priority_names[syslog_priority]
        # Message is a string. Convert to bytes as required by RFC 5424
        # Following is done in syslog.syslog()
        # msg = msg.encode('utf-8')
        # The following is where the 3 bytes of crap come from...
        #if codecs:
        #    msg = codecs.BOM_UTF8 + msg
        syslog.syslog(syslog_priority, msg)


class MagCodeLog(object):
    """
    Generic Logging Object
    """
    def __init__(self):
        self._init_log_handlers()

    def _init_log_handlers(self):
        """
        Initialise basic logging
        """
        # Log Formatters
        self._configure_log_formatters()
        # set logging level
        self.set_logging_level()

        # Set up stderr log handler
        self._configure_stderr_logging()

        if (settings['process_type'] == PROCESS_TYPE_DAEMON):
            self.configure_syslog_logging()

    def _configure_stderr_logging(self):
        """
        Set up stderr log handler
        """
        # Remove any existing handler
        if (hasattr(self, 'stderr_handler') and self.stderr_handler):
            logging.root.removeHandler(self.stderr_handler)

        # Add new handler depending on process_type or debug()
        if (debug()):
            self.stderr_handler = logging.StreamHandler()
            self.stderr_handler.setFormatter(self.log_formatter)
            logging.root.addHandler(self.stderr_handler)
        elif (settings['process_type'] == PROCESS_TYPE_DAEMON):
            self.stderr_handler = logging.StreamHandler()
            self.stderr_handler.setFormatter(self.stderr_formatter)
            logging.root.addHandler(self.stderr_handler)
        elif (settings['process_type'] == PROCESS_TYPE_UTILITY):
            self.stderr_handler = logging.StreamHandler()
            self.stderr_handler.setFormatter(self.stderr_formatter)
            logging.root.addHandler(self.stderr_handler)
        elif (settings['process_type'] == PROCESS_TYPE_WSGI):
            self.stderr_handler = logging.StreamHandler()
            self.stderr_handler.setFormatter(self.wsgi_formatter)
            logging.root.addHandler(self.stderr_handler)


    def _configure_log_formatters(self):
        """
        Configure the log formaters
        """
        self.fs = settings['log_message_format']
        self.sfs = settings['syslog_message_format']
        self.sfe = settings['stderr_message_format']
        self.sfw = settings['wsgi_message_format']
        self.dfs = settings['log_message_date_format']
        self.log_formatter = logging.Formatter(self.fs, self.dfs)
        self.stderr_formatter = logging.Formatter(self.sfe, None)
        self.syslog_formatter = logging.Formatter(self.sfs, None)
        self.wsgi_formatter = logging.Formatter(self.sfw, None)

    def set_logging_level(self):
        """
        Set logging level
        """
        if (debug()):
            logging.root.setLevel(MAGLOG_DEBUG)
        else:
            logging.root.setLevel(settings['log_level'])
   
    def _remove_all_log_handlers(self):
        if (hasattr(self, 'stderr_handler') and self.stderr_handler):
            logging.root.removeHandler(self.stderr_handler)
        if (hasattr(self, 'syslog_handler') and self.syslog_handler):
            logging.root.removeHandler(self.syslog_handler)
        if (hasattr(self, 'logfile_handler') and self.logfile_handler):
            logging.root.removeHandler(self.logfile_handler)

    def reconfigure_logging(self):
        """
        Reconfigures logging after configuration read on startup
        """
        #self._remove_all_log_handlers()
        self._init_log_handlers()
        #self.set_logging_level()

    def configure_syslog_logging(self):
        """
        Configure syslog logging

        Typically done for daemons
        """
        # Set up syslog logging
        if (hasattr(self, 'syslog_handler') and self.syslog_handler):
            logging.root.removeHandler(self.syslog_handler)
        if (settings['syslog_facility']):
            self.syslog_handler = MagCodeSysLogHandler(
                    facility = settings['syslog_facility'])
            self.syslog_handler.setFormatter(self.syslog_formatter)
            logging.root.addHandler(self.syslog_handler)
  
    def configure_file_logging(self):
        """
        Configure file logging

        This is typically done after we have syslog running or stderr
        and after processing the configuration file in a daemon process
        """
        if (hasattr(self, 'logfile_handler') and self.logfile_handler):
            logging.root.removeHandler(self.logfile_handler)
        if (settings['log_file']):
            try:
                maxBytes = 1024 * get_numeric_setting(
                                    'log_file_max_size_kbytes', int)
                logfile_handler = logging.handlers.RotatingFileHandler(
                        filename=settings['log_file'],
                        maxBytes=maxBytes,
                        backupCount=settings['log_file_backup_count'])
            except IOError as e:
                log_error("%s - %s." % (e.filename, e.strerror))
                return
            logfile_handler.setFormatter(self.log_formatter)
            logging.root.addHandler(logfile_handler)
            self.logfile_handler = logfile_handler

    def remove_daemon_stderr_logging(self):
        """
        Remove stderr logging prior to forking away to daemon land
        """
        if (not debug()):
            logging.root.removeHandler(self.stderr_handler)


def setup_logging():
    """
    Set up logging on application start up
    """
    global log_object
    if (not log_object):
        log_object = MagCodeLog()

def reconfigure_logging():
    """
    Reconfigure logging after reading configuration file
    """
    global log_object
    log_object.reconfigure_logging()

def setup_file_logging():
    """
    Set up file logging, typically once configuration file is read
    """
    global log_object
    log_object.configure_file_logging()

def setup_syslog_logging():
    """
    Setup syslog logging. Some Utilites may want this.
    """
    global log_object
    log_object.configure_syslog_logging()
    
def remove_daemon_stderr_logging():
    """
    Remove stderr logging prior to forking away to daemon land
    """
    global log_object
    log_object.remove_daemon_stderr_logging()


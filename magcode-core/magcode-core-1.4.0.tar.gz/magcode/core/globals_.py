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
"""Application Global Data

This module is set up to contain application global data, such as process name,
configuration file, log function name etc.
"""


import os
import sys
import syslog
import logging
# Some helper stuff to make more sense of mess in logging module
from logging import log as log
from logging import critical as log_critical
from logging import critical as log_fatal
from logging import error as log_error
from logging import error as log_err
from logging import warning as log_warning
from logging import warning as log_warn
from logging import info as log_info
from logging import debug as log_debug
from logging import BASIC_FORMAT
from logging import CRITICAL as MAGLOG_CRITICAL
from logging import CRITICAL as MAGLOG_FATAL
from logging import ERROR as MAGLOG_ERROR
from logging import ERROR as MAGLOG_ERR
from logging import WARNING as MAGLOG_WARNING
from logging import WARNING as MAGLOG_WARN
from logging import INFO as MAGLOG_INFO
from logging import DEBUG as MAGLOG_DEBUG
from logging import NOTSET as MAGLOG_NOTSET
from logging import NOTSET as MAGLOG_NONE

# For setproctitle() further down - a nice to have for admin and ps
try:
    from setproctitle import setproctitle
    setproctitle_support = True
except ImportError:
    setproctitle_support = False



process_name = os.path.basename(sys.argv[0])
# Dictionary where we store program settings
settings = {}
# Dictionary where we store golbal data
# Split from settings as it will more than strings, ie include python
# instatated objects.  Means we can dump settings to a configuration file!
data = {}
_uname = os.uname()
_os_family = _uname[0]
hostname_fqdn = _uname[1]
hostname = _uname[1].split('.',1)[0]
settings['hostname'] = hostname
if (_os_family == "FreeBSD"):
        CONFIG_DIR = "/usr/local/etc/magcode"
        VAR_LIB_DIR = "/var/lib/magcode"
        LOG_DIR = "/var/log/magcode"
        RUN_DIR = "/var/run/magcode"
        CONFIG_FILE = CONFIG_DIR + "/magcode.conf"
        PID_FILE = RUN_DIR + "/" + process_name + ".pid"
        LOG_FILE = LOG_DIR + process_name + ".log"
        PANIC_LOG = LOG_DIR + process_name + "-panic.log"
elif(_os_family == "Linux"):
        CONFIG_DIR = "/etc/magcode"
        VAR_LIB_DIR = "/var/lib/magcode"
        LOG_DIR = "/var/log/magcode"
        RUN_DIR = "/var/run/magcode"
        CONFIG_FILE = CONFIG_DIR + "/magcode.conf"
        PID_FILE = RUN_DIR + "/" + process_name + ".pid"
        LOG_FILE = LOG_DIR + process_name + ".log"
        PANIC_LOG = LOG_DIR + process_name + "-panic.log"
else:
    raise Exception("Unrecognised OS '%s'" % _os_family)
settings['os_family'] = _os_family

DEBUG_LEVEL_NONE = 0
# Process debug log messages only
DEBUG_LEVEL_NORMAL = 1
# Include SQL ALchemy SQL debug messages
DEBUG_LEVEL_VERBOSE = 2
# Include SQL ALchemy debug messages (includes SQL)
DEBUG_LEVEL_EXTREME = 3
settings['debug_level'] = DEBUG_LEVEL_NONE

# Directory settings
settings['config_dir'] = CONFIG_DIR
settings['log_dir'] = LOG_DIR
settings['var_lib_dir'] = VAR_LIB_DIR
settings['run_dir'] = RUN_DIR

# File path settings
settings['config_file'] = CONFIG_FILE
settings['pid_file'] = PID_FILE
settings['log_file'] = LOG_FILE
settings['panic_log'] = PANIC_LOG
# Event Queue PID file location
# set to what ever needed in application globals_.py
settings['event_queue_pid_file'] = settings['pid_file'] 

settings['run_as_user'] = ''        # Initialise to '' for config file checks

# Process type settings
PROCESS_TYPE_UTILITY = "utility"
PROCESS_TYPE_DAEMON = "daemon"
PROCESS_TYPE_WSGI = "wsgi"
settings['process_type'] = PROCESS_TYPE_UTILITY
# Something to see ti daemon reconfiguring
settings['daemon_canary'] = "pink polka dot"

# Some process_name trickery to handle editor choices via /etc/passwd
editor_sep = process_name.rfind('~')
settings['editor_flag'] = ''
if editor_sep > -1:
    settings['editor_flag'] = process_name[editor_sep+1:]
    process_name = process_name[:editor_sep]

# Set our process title to something sensible other than python3.x !
if setproctitle_support:
    setproctitle(process_name)
settings['process_name'] = process_name

# Preconvert settings list for use in code start up
settings['preconvert_bool_settings'] = ''
settings['preconvert_int_settings'] = ''
settings['preconvert_float_settings'] = ''

# logging.py settings
# Initialise Default Log settings
settings['syslog_facility'] = syslog.LOG_USER
settings['log_level'] = logging.INFO
settings['log_file_max_size_kbytes'] = 2048
settings['log_file_backup_count'] = 7
log_message_format = "%(asctime)s " + process_name \
            + "[%(process)d]: " + "%(levelname)s - %(message)s"
settings['log_message_format'] = log_message_format
syslog_message_format = "%(levelname)s - %(message)s"
settings['syslog_message_format'] = syslog_message_format
log_message_date_format = "%b %e %H:%M:%S"
settings['log_message_date_format'] = log_message_date_format
stderr_message_format = process_name + ": %(message)s"
settings['stderr_message_format'] = stderr_message_format
wsgi_message_format = process_name + " (pid=%(process)d, threadid=%(thread)d): %(levelname)s - %(message)s"
settings['wsgi_message_format'] = wsgi_message_format

# JSON RPC settings
settings['jsonrpc_max_content_length'] = 102400
settings['jsonrpc_error_stack_trace'] = False

# system_editor_pager.py
settings['diff_args'] = '-uNw'
settings['pager_args'] = ''
settings['tail_args'] = '-n +3'
if (settings['os_family'] == "Linux"):
    settings['editor'] = '/usr/bin/rvim'
    settings['editor_rvim'] = '/usr/bin/rvim'
    settings['editor_rnano'] = '/bin/rnano'
else:
    settings['editor'] = '/usr/local/bin/rvim'
    settings['editor_rvim'] = '/usr/local/bin/rvim'
    settings['editor_rnano'] = '/usr/local/bin/rnano'
settings['pager'] = '/usr/bin/less'
settings['admin_group_list'] = 'sudo root wheel'

# database/event.py
settings['event_queue_threads'] = 3
# Processor threads never time out
settings['event_queue_thread_timeout'] = None
# Maximum queue size
settings['event_queue_maxsize'] = 50
# Event queue session transactions per Session.close()
settings['event_queue_session_transactions'] = 1000
if not settings.get('event_queue_fkey_columns'):
    settings['event_queue_fkey_columns'] = ''

# Utility functions
def debug():
    """
    utility function to return if debugging or not
    """
    return (settings['debug_level'] > DEBUG_LEVEL_NONE)

def debug_verbose():
    """
    utility function to return if verbose debugging or not
    """
    return (settings['debug_level'] >= DEBUG_LEVEL_VERBOSE)

def debug_extreme():
    """
    utility function to return if extreme debugging or not
    """
    return (settings['debug_level'] >= DEBUG_LEVEL_EXTREME)

def str_exc(exc):
    return exc.__class__.__name__ + ': ' + str(exc)

# Sort out which logging function to use - command line tools set log level
# to critical as they can turn off log to stderr in favour of their 
# own messages 
def startup_log_func(*args):
    if (settings['process_type'] == PROCESS_TYPE_UTILITY): 
        # Set up for zone_tool
        return log_critical(*args)
    else:
        return log_error(*args)



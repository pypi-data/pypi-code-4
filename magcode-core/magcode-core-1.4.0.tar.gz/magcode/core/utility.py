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
"""
Utility functions
"""


import configparser
import errno
import socket
import os
import re
from subprocess import check_output
from subprocess import CalledProcessError

from magcode.core.globals_ import *

class MagCodeConfigError(Exception):
    """
    Exception for keys in configuration file that are not in settings array."
    """
    pass

def core_read_config(config_section=None):
    """
    Read in configuration from appropriate configuration section
    """
    # Work out configuration section that we want to read
    if (config_section):
        pass
    elif (settings.get('config_section')):
        config_section = settings.get('config_section')
    else:
        config_section = process_name

    config = configparser.ConfigParser()
    try:
        config_file = open(settings['config_file'], 'rt')
        config.read_file(config_file)
        new_settings = [item for item in config.items(section=config_section)]
    except (IOError,OSError) as exc:
        startup_log_func("%s - %s." % (exc.filename, exc.strerror))
        raise exc

    except (configparser.Error) as exc:
        startup_log_func("%s - %s"  % (settings['config_file'], exc.message))
        raise exc

    # Check that settings given in Configuration file match settings keys
    error = False
    for item in new_settings:
        key = item[0]
        if key not in settings.keys():
            error = True
            startup_log_func("%s - Key '%s' not a valid configuration item."
                        % (settings['config_file'], key))
    if (error):
        raise MagCodeConfigError("Invalid keys in config file '%s'. See log."
                                        % settings['config_file'] )

    # Update settings with new ones
    settings.update(new_settings)

    # Preconvert settings at program to prevent indeterminately timed blowups
    # program running
    for key in settings['preconvert_bool_settings'].split():
        settings[key] = get_boolean_setting(key)
    for key in settings['preconvert_int_settings'].split():
        settings[key] = get_numeric_setting(key, int)
    for key in settings['preconvert_float_settings'].split():
        settings[key] = get_numeric_setting(key, float)

def get_numeric_setting(key, type_, **kw_type_args):
    """
    Get a numeric setting from the settings dictionary.

    Will error if vaule in settings file cannot be type cast from string.
    """
    try:
        value = settings[key]
    except KeyError:
        startup_log_func("Setting '%s' does not exist" % key)
        sys.exit(os.EX_SOFTWARE)
    if type(value) is type_:
        # if already converted, just directly return value
        return value
    try:
        value = type_(value, **kw_type_args)
    except ValueError:
        startup_log_func("Can't convert value '%s' "
                    "- setting '%s' requires a %s value"
                    % (value, key, str(type_)))
        sys.exit(os.EX_CONFIG)
    return value

_true_strings = ('true', 'on', 'yes', '1', 'up', 'enable', 'enabled')
_false_strings = ('false', 'off', 'no', '0', 'down', 'disable', 
                        'disabled')
_bool_strings = _true_strings + _false_strings

def get_boolean_setting(key):
    """
    Get a boolean setting from the settings dictionary.
    """
    try:
        value = settings[key]
    except KeyError:
        startup_log_func("Setting '%s' does not exist" % key)
        sys.exit(os.EX_SOFTWARE)
    if type(value) is bool:
        # Deal with direct Boolean assignment in a globals_ file
        return value
    if type(value) is str:
        # Parse a string
        if (str(value).lower() in _true_strings):
            return True
        elif (str(value).lower() in _false_strings):
            return False
    startup_log_func("Can't convert value '%s' "
                "- setting '%s' requires value in %s"
                    % (value, key, _bool_strings))
    sys.exit(os.EX_CONFIG)
    
def send_signal(pid_file_name, signal):
    """
    Check if another daemon process is around

    Returns True if we are already running, false if it is another process
    """
    exception = None
    try:
        pid_file = open(pid_file_name,'r')
        pid = int(pid_file.readline().strip())
        pid_file.close()
        # The following throws exceptions if process does not exist etc!
        # Sending signal 0 does not touch process, but  call succeeds
        # if it exists
        os.kill(pid, signal)
        return True
    except ValueError as e:
        # Error from int() type conversion above
        log_error("%s - %s" % (settings['pid_file'], e))
        return False
    except IOError as e:
        # File IO causes this
        if (e.errno in (errno.ENOENT,)):
            return False
        log_error("Could not access PID file '%s' - %s."
                  % (e.filename, e.strerror))
        return False
    except OSError as e:
        # This exception is from kill()
        if (e.errno in (errno.ESRCH,)):
            log_error("Process '%s' does not exist." % pid)
            return False
        if (e.errno in (errno.EPERM,)):
            log_error("Don't have permission to signal process '%s'." % pid)
            return False
        log_error("Undocumented error '%s' sending signal '%s' to process '%s'."
                    % (errno.errorcode[e.errno], signal, pid))
        return False
    except Exception:
        log_error("Unexpected error: %s" % sys.exc_info()[1])
        return False

def connect_test_address(name_address, port):
    """
    Test given name/address for connectability.  Connect failure
    causes exception handled further up
    """
    sockaddr = None
    while True:
        # Loop to handle signal interruption...
        try:
            (family, socktype, proto, canonname, sockaddr)\
                 = socket.getaddrinfo(name_address,
                                        port,
                                        proto=socket.SOL_TCP)[0]
            sock = socket.socket(family=family, type=socktype, proto=proto)
            sock.settimeout(0.25)
            sock.connect(sockaddr)
            sock.close()
            break
        except (IOError, OSError) as exc:
            if exc.errno not in (errno.EINTR, errno.EAGAIN):
                raise(exc)
    return sockaddr[0]

# Constant stuff for handling IP address discovery
_re_iface_inet_match = re.compile(r'^\s+inet[ 46]')
_re_iface_ipv4addr_match = re.compile(r'^\s+inet4{0,1} ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*$')
_re_iface_ipv6addr_match = re.compile(r'^\s+inet6 ([:0-9a-fA-F]+).*$')
_re_iface_lo_addr_match = re.compile(r'^127\.[\.0-9]+$|^::1$')
_re_iface_ll_addr_match = re.compile(r'^fe[89ab][:0-9a-f]+$|^169\.254[\.0-9]+$',
                                    flags=re.IGNORECASE)
if settings['os_family'] == 'Linux':
    _if_cmd = ['ip', 'addr']
else:
    _if_cmd = ['ifconfig' , '-a']

def get_configured_addresses(with_loopback=False, with_link_local=False):
    """
    Return a list of a machines conifgured addresses. 
    
    Optionally with loopback and link local addresses.
    """
    ifcmd_output = check_output(_if_cmd, universal_newlines=True).splitlines()
    ifcmd_output = [line for line in ifcmd_output 
                    if _re_iface_inet_match.search(line)]
    ifcmd_output = [_re_iface_ipv4addr_match.sub(r'\1', line) 
                        for line in ifcmd_output]
    ifcmd_output = [_re_iface_ipv6addr_match.sub(r'\1', line) 
                        for line in ifcmd_output]
    if not with_loopback:
        ifcmd_output = [line for line in ifcmd_output 
                    if not _re_iface_lo_addr_match.search(line)]
    if not with_link_local:
        ifcmd_output = [line for line in ifcmd_output 
                    if not _re_iface_ll_addr_match.search(line)]
    return ifcmd_output

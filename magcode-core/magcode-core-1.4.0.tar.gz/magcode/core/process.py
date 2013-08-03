#!/usr/bin/env python3.2
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
This module contains the addon functionality to help a process become a daemon.

It is implemented in a classful manner, with various methods performing the
requisite behaviour. Its a bit rough, but it gets the job done.
"""

import os
import sys
import pwd
import errno
import signal
import time
import resource
import configparser
from getopt import gnu_getopt
from getopt import getopt
from getopt import GetoptError
from fcntl import fcntl
from fcntl import F_GETFL

# A bit of nice stuff to set up ps output as much as we can...
try:
    from setproctitle import getproctitle
    setproctitle_support = True
except ImportError:
    setproctitle_support = False

from magcode.core.globals_ import *
from magcode.core.logging import setup_logging
from magcode.core.logging import reconfigure_logging
from magcode.core.logging import setup_file_logging
from magcode.core.logging import remove_daemon_stderr_logging
from magcode.core.utility import core_read_config
from magcode.core.utility import MagCodeConfigError

# Default working directory
WORKDIR = "/"
# Process Umask
# Daemonization process sets this to 0000, but set to something sensible
# as we don't want world writable files being created from any daemons!!!
#UMASK = 0o0000
UMASK = 0o0022

# Default Max FDs
MAXFD = 1024
REDIRECT_TO = "/dev/null"
# Default Command line help messages
STUB_USAGE_MESSAGE = "Usage: %s [-dhv] [-c config_file] [-r rpdb2_wait] (Stub 'usage_short()' msg)"
STUB_COMMAND_DESCRIPTION = "Command description (Stub 'usage_full()' message.)"



class BaseCmdLineArg(object):
    """
    Ancestor primitive to establish universal properties of command line
    argument objects.  Mainly used as it gives an ancestor type we can 
    test for.
    """

    def __init__(self, short_arg, help_text, long_arg=None, *args, **kwargs):
        """
        Initialise object.  Short_arg must have ':' appended if value
        required. Long_arg must have '=' appended if value is required.
        """
        self.short_arg = short_arg
        if (long_arg):
            self.long_arg = long_arg
        else:
            self.long_arg = '   '
        self.help_text = help_text

    def process_arg(self, process, argument=None, value=None,
                    *args, **kwargs):
        """
        Stub method for processing an argument. 
        
        process is the process class instance
        Processes argument, then returns if argument processed successfully,
        otherwise exits program.
        """
        process.usage_short()
        sys.exit(os.EX_USAGE)

class HelpCmdLineArg(BaseCmdLineArg):
    """
    Process help command line argument
    """
    def __init__(self):
        BaseCmdLineArg.__init__(self,
                                short_arg='h',
                                long_arg='help',
                                help_text='help message')

    def process_arg(self, process, *args, **kwargs):
        """
        Process the help argument
        """
        process.usage_full()
        sys.exit(os.EX_OK)

class BooleanCmdLineArg(BaseCmdLineArg):
    """
    Process boolean command Line setting

    short_arg - single letter cmd line argument
    long_arg - single letter cmd line argument (optional)
    help_text - single line help text
    settings_key - key to be used in settings dictionary
    settings_defalut_value - default value of setting
    settings_set_value - setting of value if switch given.
    """
    def __init__(self, short_arg, help_text,
            settings_key,
            settings_default_value,
            settings_set_value,
            long_arg=None,

            *args, **kwargs):
        BaseCmdLineArg.__init__(self,
                                short_arg=short_arg,
                                long_arg=long_arg,
                                help_text=help_text)
        self.settings_key = settings_key
        self.settings_default_value = settings_default_value
        self.settings_set_value = settings_set_value
        # Initialise settings dictionary to default value
        settings[settings_key] = settings_default_value

    def process_arg(self, *args, **kwargs):
        """
        Change the setting if command line argument given
        """
        settings[self.settings_key] = self.settings_set_value

class VerboseCmdLineArg(BooleanCmdLineArg):
    """
    Process verbose command Line setting
    """
    def __init__(self):
        BooleanCmdLineArg.__init__(self,
                                short_arg='v',
                                long_arg='verbose',
                                help_text='verbose output',
                                settings_key = 'verbose',
                                settings_default_value = False,
                                settings_set_value = True)

class MemoryDebugCmdLineArg(BooleanCmdLineArg):
    """
    Process Garbage Collector command line setting
    """
    def __init__(self):
        BooleanCmdLineArg.__init__(self,
                                short_arg='b',
                                long_arg='memory-debug',
                                help_text='memory debug output',
                                settings_key = 'memory_debug',
                                settings_default_value = False,
                                settings_set_value = True)


class ConfigCmdLineArg(BaseCmdLineArg):
    """
    Handle configuration file setting
    """
    def __init__(self):
        BaseCmdLineArg.__init__(self, short_arg='c:',
                                long_arg="config-file=",
                                help_text="set configuration file")
        # Don't have to set default value here as it is set in 
        # magcode.core.globals_

    def process_arg(self, process, value, *args, **kwargs):
        """
        Set configuration file name
        """
        settings['config_file'] = value 

class ForceCmdLineArg(BooleanCmdLineArg):
    """
    Process force command Line setting
    """
    def __init__(self):
        BooleanCmdLineArg.__init__(self,
                            short_arg='f',
                            long_arg='force',
                            help_text="Force operation, say if calling from a script",
                            settings_key = 'force_arg',
                            settings_default_value = False,
                            settings_set_value = True)


class Rpdb2WaitCmdLineArg(BaseCmdLineArg):
    """
    Handle waiting for rpdb2 in debug mode
    """
    def __init__(self):
        BaseCmdLineArg.__init__(self, short_arg='r:',
                                long_arg="rpdb2-wait=",
                                help_text="Wait for rpdb2 (seconds)")
        settings['rpdb2_wait'] = None

    def process_arg(self, process, value, *args, **kwargs):
        """
        Set time out for rpdb2
        """
        settings['rpdb2_wait'] = value 


class DebugCmdLineArg(BaseCmdLineArg):
    """
    Process debug command line argument
    """
    debug_levels = {
        'none': DEBUG_LEVEL_NONE,
        'zero': DEBUG_LEVEL_NONE,
        'nada': DEBUG_LEVEL_NONE,
        'zilch': DEBUG_LEVEL_NONE,
        'no': DEBUG_LEVEL_NONE,
        'false': DEBUG_LEVEL_NONE,
        'process': DEBUG_LEVEL_NORMAL,
        'normal': DEBUG_LEVEL_NORMAL,
        'norm': DEBUG_LEVEL_NORMAL,
        'yes': DEBUG_LEVEL_NORMAL,
        'true': DEBUG_LEVEL_NORMAL,
        'verbose': DEBUG_LEVEL_VERBOSE,
        'verb': DEBUG_LEVEL_VERBOSE,
        'sql': DEBUG_LEVEL_VERBOSE,
        'extreme': DEBUG_LEVEL_EXTREME,
        'everything': DEBUG_LEVEL_EXTREME,
        'nuts': DEBUG_LEVEL_EXTREME,
    }

    def __init__(self):
        BaseCmdLineArg.__init__(self, short_arg='d:', long_arg='debug=',
            help_text='set debug level {0-3|none|normal|verbose|extreme}')
        self.debug_levels = DebugCmdLineArg.debug_levels
        settings['debug_level'] = DEBUG_LEVEL_NONE

    def process_arg(self, process, value, *args, **kwargs):
        """
        Process debug level argument
        """
        try:
            val = int(value)
            if (val < DEBUG_LEVEL_NONE
                    and val > DEBUG_LEVEL_EXTREME):
                process.usage_full()
                sys.exit(os.EX_USAGE)
            settings['debug_level'] = val
        except ValueError:
            if (value in DebugCmdLineArg.debug_levels.keys()):
                settings['debug_level'] = DebugCmdLineArg.debug_levels[value]
            else:
                process.usage_full()
                sys.exit(os.EX_USAGE)

DEFAULT_CMDLINE_ARG_LIST = [DebugCmdLineArg(),
                            HelpCmdLineArg(),
                            MemoryDebugCmdLineArg(),
                            ConfigCmdLineArg(),
                            VerboseCmdLineArg()]


class ProcessCmdLine(object):
    """
    Ancestor class to set up command line argument handling
    """

    def __init__(self, usage_message=STUB_USAGE_MESSAGE, 
            command_description=STUB_COMMAND_DESCRIPTION,
            cmdline_arg_list = DEFAULT_CMDLINE_ARG_LIST,
            use_gnu_getopt=True,
            *args, **kwargs):
        """
        Initialise command line usage help messages, and command line
        argments
        """
        self.usage_message = usage_message
        self.command_description = command_description
        self.cmdline_arg_list = cmdline_arg_list
        self.use_gnu_getopt = use_gnu_getopt
        super().__init__(*args, **kwargs)

    def parse_args(self, argv=sys.argv, argc=len(sys.argv)):
        """
        Command line argument parsing

        Returns arguments left over from processing

        Using getopt.gnu_getopt() as argparse module is too new, 
        and gnu_getopt() allows us to easily go back to Python 2.x 
        This also is in line with are tight control of process start up
        and daemonizing.
        """
        # 1. Gather data on command line argments and create callback array
        short_opts = ''
        long_opts = []
        callback_dict = {}
        for arg_obj in self.cmdline_arg_list:
            short_opts += arg_obj.short_arg
            long_opts.append(arg_obj.long_arg)
            # need to strip trailing characters specifying that argument
            # must be given
            callback_dict[arg_obj.short_arg.rstrip(':')] = arg_obj
            callback_dict[arg_obj.long_arg.rstrip('=')] = arg_obj

        # Call getopt and process each argument via its callback method
        try:
            if self.use_gnu_getopt:
                opts, argv_left = gnu_getopt(argv[1:], short_opts, long_opts)
            else:
                opts, argv_left = getopt(argv[1:], short_opts, long_opts)

        except GetoptError:
            self.usage_short()
            sys.exit(os.EX_USAGE)

        for arg, val in opts:
            # strip '-' from a
            arg = arg.lstrip('-')
            if (arg not in callback_dict.keys()):
                self.usage_short()
                sys.exit(os.EX_USAGE)
            callback_dict[arg].process_arg(process=self,
                    argument=arg, value=val)

        # return unprocessed arguments.  These are generally of interest
        # for main_process
        return argv_left

    def parse_argv_left(self, argv_left):
        """
        Handle any arguments left after processing all switches

        Override in application if needed.
        """
        if (len(argv_left) != 0):
            self.usage_short()
            sys.exit(os.EX_USAGE)

    def usage_short(self, tty_file=sys.stderr):
        """
        Stub short help message routine
        """
        print(self.usage_message % process_name, file=tty_file)

    def usage_full(self, tty_file=sys.stdout):
        """
        Stub verbose help message routine
        """
        self.usage_short(tty_file=tty_file)
        print("\n  %s\n" % self.command_description, file=tty_file)
        for arg_obj in self.cmdline_arg_list:
            print("  -%s, --%-16s  %s" % (arg_obj.short_arg.rstrip(':'),
                                        arg_obj.long_arg.rstrip('='),
                                        arg_obj.help_text))

class Process(ProcessCmdLine):
    """
    Main command line utility process class

    Contains all the code for a commandline utility sans the command line
    processing handled above.
    """
    def main_process(self):
        """
        Dummy main_process that can be overridden
        Typically does what ever, and then calls
        sys.exit()
        """
        log_info ("Hello World")
        sys.exit(os.EX_OK)

    def main(self, argv=sys.argv, argc=len(sys.argv)):
        """
        Cish command line utility type main() that can be overridden
        """
        # set process tupe
        settings['process_type'] = PROCESS_TYPE_UTILITY
        argv_left = self.parse_args(argv, argc)
        self.parse_argv_left(argv_left)
        setup_logging()
        self.read_config()
        self.main_process()

    def read_config(self, config_section = None):
        """
        Read configuration from an ini style configuration file into
        settings dict.

        config_section - Name of configuration section to be read.
        Method can be overridden in real main process.  Have a look
        at the python module configparser for documentation. File has to
        have a '[blah]' section header, and supports a [DEFAULT] section. 
        """
        try:
            core_read_config(config_section)
        # Handle file opening and read errors
        except (IOError,OSError) as e:
            if (e.errno == errno.EPERM or e.errno == errno.EACCES):
                sys.exit(os.EX_NOPERM)
            else:
                sys.exit(os.EX_IOERR)

        # Handle all configuration file parsing errors
        except configparser.Error as e:
            sys.exit(os.EX_CONFIG)
        
        except MagCodeConfigError as e:
            sys.exit(os.EX_CONFIG)

    def check_if_root(self):
        """
        Check that we are running as root, if not exit with message.

	ProcessDaemon bleow overrides this.  It is here for script utilities.
        """
        # check that we are root for file writing permissions stuff
        if (os.geteuid() != 0 ):
            log_error("Only root can execute this command")
            sys.exit(os.EX_NOPERM)
    
    def check_or_force(self, exit_on_no=True):
        """
        Ask user if they want to go ahead.  
        
        Added as it is used a lot.  Need to initialise ForceCmdLineArg() for
        use in a process.
        """
        if not settings['force_arg']:
            print(8*' ' + "Do really you wish to do this?")
            answer = ''
            while not answer:
                answer = input('\t--y/[N]> ')
                if answer in ('n', 'N', ''):
                    if exit_on_no:
                        sys.exit(os.EX_TEMPFAIL)
                    return False
                elif answer in ('y', 'Y'):
                    return True
                answer = ''
                continue
        return True

class DaemonOperations(object):
    """
    Daemon Operations Mix-in Container class

    This optionally does not close all file descriptors as this 
    kills the Python logging module...

    Based on recipe up at 
    http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way
    under the PSF license.
    References:
    1) Advanced Programming in the Unix Environment: W. Richard Stevens
    2) Unix Programming Frequently Asked Questions:
        http://www.erlenstar.demon.co.uk/unix/faq_toc.html

    """
    def _init_pwd(self):
        """
        Initialise run_as_user_pwd information
        """
        run_as_user = settings.get('run_as_user')
        if (not run_as_user):
            return

        try:
            self.run_as_user_pwd = pwd.getpwnam(run_as_user)
        except KeyError as e:
            log_error("run_as_user '%s' not found. Exiting daemon."
                      % run_as_user)
        
    def check_if_running(self):
        """
        Check if another daemon process is around

        Returns True if we are already running, false if it is another process
        """
        exception = None
        try:
            pid_file = open(settings['pid_file'],'r')
            old_pid = int(pid_file.readline().strip())
            pid_file.close()
            # The following throws exceptions if process does not exist etc!
            # Sending signal 0 does not touch process, but  call succeeds
            # if it exists
            os.kill(old_pid, 0)
            if (self.i_am_daemon()):
                return True
        except ValueError as e:
            # Error from int() type conversion above
            log_error("%s - %s" % (settings['pid_file'], e))
        except IOError as e:
            # File IO causes this
            if (e.errno in (errno.ENOENT,)):
                return False
            log_error("Could not access PID file '%s' - %s."
                      % (e.filename, e.strerror))
        except OSError as e:
            # This exception is from kill()
            if (e.errno in (errno.ESRCH,)):
                return False
            log_error("Another process is already running - %s." % old_pid)
        except:
            log_error("Unexpected error: %s" % sys.exc_info()[1])
            sys.exit(os.EX_OSERR)
        else:
            log_error("Another process is already running - %s." % old_pid)
       
        # If we can't run at all, exit!
        sys.exit(os.EX_CANTCREAT)

    def create_pid_file(self):
        """
        Create PID file for this process
        """
        try:
            pid_file = open(settings['pid_file'], 'w')
            pid_file.write("%s\n" % os.getpid())
            pid_file.close()
        except IOError as e:
            log_error("%s - %s." % (e.filename, e.strerror))
            if (e.errno == errno.EPERM or e.errno == errno.EACCES):
                sys.exit(os.EX_NOPERM)
            else:
                sys.exit(os.EX_IOERR)
        
    def _do_forks(self):
        """
        Daemon fork operation

        Split out for debugging
        """
        # Keep track of where we are
        log_debug('0th fork(): PID: %s PPID: %s SID: %s PGID: %s' 
                % (os.getpid(), os.getppid(), os.getsid(0), os.getpgid(0)))
        # First fork so that parent can exit
        try:
            pid = os.fork()
        except OSError as e:
            # log or stderr something here
            # raise Exception "%s [%d]" % (e.strerror, e.errno)
            os.exit(os.EX_OSERR)

        if (pid == 0):
            # First child
            log_debug('1st fork(): PID: %s PPID: %s SID: %s PGID: %s' 
                % (os.getpid(), os.getppid(), os.getsid(0), os.getpgid(0)))
            # Become session leader
            os.setsid()

            # Keep track of things
            log_debug('1st fork(), setsid(): PID: %s PPID: %s SID: %s PGID: %s' 
                % (os.getpid(), os.getppid(), os.getsid(0), os.getpgid(0)))

            # Optionally ignore SIGHUP
            import signal
            signal.signal(signal.SIGHUP, signal.SIG_IGN)

            # Second fork to orphan child and detach from controlling
            # terminal
            try:
                pid = os.fork()
            except OSError as e:
                # log or stderr something here?
                # raise Exception "%s [%d]" % (e.strerror, e.errno)
                sys.exit(os.EX_OSERR)

            if (pid != 0):
                # use _exit() as it does not pfaff around with pythonic cleanup
                # which is not needed this early...
                # Exit second parent
                os._exit(os.EX_OK)
        else:
            # Exit first parent
            os._exit(0)

        # Keep track of stuff
        log_debug('2nd fork(): PID: %s PPID: %s SID: %s PGID: %s' 
                % (os.getpid(), os.getppid(), os.getsid(0), os.getpgid(0)))


    def _close_fds(self, fd_top= None):
        """
        Close all FDs that are NOT needed.

        Split out from daemonize for debug purposes
        """
        # Close all open file descriptors
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = MAXFD
        
        # Iterate through and close all file descriptors.
        for fd in range(0, maxfd):
            if (fd_top):
                # skip python logging/syslog fds etc!
                if (fd <= fd_top and fd > 2):
                    continue
            try:
                os.close(fd)
            except OSError:     # ERROR, fd wasn't open to begin with (ignored)
                pass

        # Redirect stderr, stdout stdin
        # This call to open is guaranteed to return the lowest file 
        # descriptor, which will be 0 (stdin), since it was closed above.
        os.open(REDIRECT_TO, os.O_RDWR) # standard input (0)
        
        # Duplicate standard input to standard output and standard error.
        os.dup2(0, 1)                   # standard output (1)
        os.dup2(0, 2)

    def _open_panic_log(self, close_all_fds):
        """
        Open the panic log

        Hidden class split out for debug purposes
        Returns fd_top to daemonize method
        """
        fd_top = 0
        if not(close_all_fds):
            try:
                self.panic_log = open(settings['panic_log'], 'w')
            except IOError as e:
                log_error("%s - %s." % (e.filename, e.strerror))
                if (e.errno == errno.EPERM or e.errno == errno.EACCES):
                    sys.exit(os.EX_NOPERM)
                else:
                    sys.exit(os.EX_IOERR)
            fd_top = self.panic_log.fileno()

        return (fd_top)
    
    def _reduce_privilege(self):
        """
        Drop privileges to runas user
        """
        if (not hasattr(self, 'run_as_user_pwd')):
            return

        new_uid = self.run_as_user_pwd.pw_uid
        new_gid = self.run_as_user_pwd.pw_gid
        new_uname = self.run_as_user_pwd.pw_name

        log_debug('Current UID: %s GID: %s' % (os.getuid(), os.getgid()))

        if (os.geteuid() == new_uid and os.getegid() == new_gid
                and os.getuid() == new_uid and os.getgid() == new_gid):
            log_debug('Already UID: %s GID: %s' % (os.getuid(), os.getgid()))
            return

        # Change ownership of all open FDs above stderr
        # Work up to maxfd
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = MAXFD
        for fd in range(3, maxfd):
            try:
                fcntl(fd, F_GETFL)
            except IOError as e:
                if (e.errno == errno.EBADF):
                    continue
                else:
                    # Create Hell!
                    raise e
            try:
                os.fchown(fd, new_uid, new_gid)
            except OSError as e:
                if (e.errno == errno.EINVAL):
                    pass
                else:
                    raise e
        
        # Lets fix any PID file ownship issues while we are at it.  If
        # we have gotten this far, we have already checked the PID file, 
        # and another pocess is none existent (hopefully)...
        try:
            os.chown(settings['pid_file'], new_uid, new_gid)
        except OSError as e:
            if (e.errno == errno.ENOENT):
                pass
            else:
                log_error("%s - %s." % (e.filename, e.strerror))
                sys.exit(os.EX_OSERR)

        # Drop privilege
        try:
            # This call only exists in Python 2.7.1 and Python 3.2
            os.initgroups(new_uname, new_gid)
        except AttributeError:
            pass
        os.setregid(new_gid, new_gid)
        os.setreuid(new_uid, new_uid)
        log_debug('New UID: %s GID: %s' % (os.getuid(), os.getgid()))
        

    def daemonize(self, close_all_fds=False):
        """
        Daemonize a process.  
        """

        # Check to see if a daemon is already running
        self.check_if_running()

        # Check that run_as_user exists
        self._init_pwd()

        if (debug()):
            os.chdir(WORKDIR)
            os.umask(UMASK)
            self._reduce_privilege()
            # create a PID file since we are running in debug mode
            self.create_pid_file()
            # Exit function
            return

        # Turn off stderr output before we fork away
        remove_daemon_stderr_logging()

        # Open the Panic Log
        fd_top = self._open_panic_log(close_all_fds)

        # Fork away and become a daemon
        if (not self.i_am_daemon()):
            self._do_forks() 

        # we are now the second fork() child
        os.chdir(WORKDIR)
        os.umask(UMASK)

        # Close all file descriptors
        self._close_fds(fd_top)

        if (fd_top):
            # Redirect Python stderr output
            sys.stderr = self.panic_log

        # Reduce privilege
        self._reduce_privilege()

        # Write PID file
        self.create_pid_file()

    def i_am_daemon(self):
        """
        Returns whether the current process is a daemon or not
        """
        pid = os.getpid()
        sid = os.getsid(0)
        pgid = os.getpgid(0)
        ppid = os.getppid()

        if (ppid == 1  and sid == pgid and pid != sid):
            return True
        else:
            return False
    

class SignalHandler(object):
    """
    Signal handler callable object.

    __call__ method sets an internal flag, which then causes
    action() method to be executed next time around the main_process()
    loop.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialises signal handler object.  Typically sets
        flag top False
        """
        self.flag = False
    
    def __call__(self, signal_number, stack_frame, *args, **kwargs):
        """
        Signal Handling routine for handler object

        Not usually a good thing to do much in here.  A lot of output
        operations to stdout or stderr pretty dicey.
        """
        self.flag = True

    def signalled(self):
        """
        returns state of self.flag, ie whether this signal has been seen or not
        
        """
        seen = self.flag
        self.flag = False
        return seen

    def action(self):
        """
        Action method for signal handler.

        For overriding when subclassed.  Carries out main action in 
        main loop up in the while statement. Returns True if main loop should
        terminate, False otherwise.
        """
        return False

class SIGHUPHandler(SignalHandler):
    """
    Handle SIGHUP signal.

    Instance is callable for giving to signal(2).  Action method in main loop
    does exec() with our original argv, plus an argment to NOT daemonise.
    """
    def action(self):
        """
        SIGHUP action
        """
        # If debug, ignore SIGHUP aprt from log_debug message
        if (debug()):
            log_info('SIGHUP received - ignoring as in debug mode.')
            return False

        log_info('SIGHUP received - execve() to reconfigure.')
        file_path = os.path.join(sys.path[0], sys.argv[0])
        file_path = os.path.normpath(file_path)
        os.execve(file_path, sys.argv, os.environ)

class SIGTERMHandler(SignalHandler):
    """
    Handle a SIGETERM signal.

    Just make action() return True
    """
    def action(self):
        log_info('SIGTERM received - exiting process.')
        return True

class SignalBusiness(object):
    """
    A mix in class to handle signal operations

    Initialise by calling init_signals() method.  If you need more signals
    than set up by default, override this method and call it as an ancestor
    FIRST, before adding you own signals.
    """

    def init_signals(self):
        """
        Initialse signals we will use in main daemon process

        When you need more signals, override this, and call it FIRST
        in descedant method.
        """
        self.register_signal_handler(signal.SIGTERM, SIGTERMHandler())
        self.register_signal_handler(signal.SIGHUP, SIGHUPHandler())

    def register_signal_handler(self, sig, handler_instance):
        """
        Register a signal handler

        Takes a handler object, signal.SIG_DFL, or signal.SIG_IGN
        """
        if not hasattr(self, 'signal_handlers'):
            self.signal_handlers = {}
        old_instance = signal.signal(sig, handler_instance)
        # Always interrupt system calls for registered signals
        signal.siginterrupt(sig, True)
        self.signal_handlers[sig] = (handler_instance, old_instance)

    def unregister_signal_handler(self, sig):
        """
        Unregister a signal handler for a signal

        Just takes a signal
        """
        old_instance = self.signal_handlers[sig][1]
        signal.signal(sig, old_instance)
        del self.signal_handlers[sig]

    def check_signals(self):
        """
        Check and see if any registered signals have been received or not

        Returns False if a signal has asked for main loop termination
        """
        retval = True
        for signal_handler in self.signal_handlers.values():
            if (signal_handler[0] == signal.SIG_DFL 
                    or signal_handler[0] == signal.SIG_IGN):
                continue

            # We may need to do some real stuff with this signal
            if (signal_handler[0].signalled()):
                if (signal_handler[0].action()):
                    retval = False

        return retval
        



class ProcessDaemon(Process, DaemonOperations, SignalBusiness):
    """
    Main daemon process class
    """

    def __init__(self, *args, **kwargs):
        """
        Add wait for Rpdb2 to commande line
        """
        Process.__init__(self, *args, **kwargs)
        self.cmdline_arg_list.append(Rpdb2WaitCmdLineArg())
    
    def check_if_root(self):
        """
        Check if we are root

        If not, exit with an error message
        """
        if (os.geteuid() != 0 and not self.i_am_daemon()):
            print("%s: Only root can execute this program."
                    % process_name,
                file=sys.stderr)
            sys.exit(os.EX_NOPERM)
        return(0)
   
    def main_process(self):
        """
        Dummy main_process that can be overridden
        Typically loops, cleans up and calls sys.exit() on SIGTERM
        """
        
        if (settings['rpdb2_wait']):
            # a wait to attach with rpdb2...
            log_info('Waiting for rpdb2 to attach.')
            time.sleep(float(settings['rpdb2_wait']))

        log_info('program starting.')
        log_debug("The daemon_canary is: '%s'" % settings['daemon_canary'])
        # Do a nice output message to the log
        pwnam = pwd.getpwnam(settings['run_as_user'])
        if setproctitle_support:
            gpt_output = getproctitle()
        else:
            gpt_output = "no getproctitle()"
        log_debug("PID: %s process name: '%s' daemon: '%s' User: '%s' UID: %d GID %d" 
                % (os.getpid(), gpt_output, self.i_am_daemon(), pwnam.pw_name,
                    os.getuid(), os.getgid()))

        if (settings['memory_debug']):
            # Turn on memory debugging
            log_info('Turning on GC memory debugging.')
            gc.set_debug(gc.DEBUG_LEAK)

        # Process Main Loop
        while (self.check_signals()):
            sleep_time = float(settings['sleep_time'])
            log_debug("Process.main_process() - sleep(%s) seconds."
                    % sleep_time) 
            time.sleep(sleep_time)

        log_info('Exited main loop - process terminating normally.')
        sys.exit(os.EX_OK)

    def main(self, argv=sys.argv, argc=len(sys.argv)):
        """
        Cish daemon type main() that can be overridden
        """
        settings['process_type'] = PROCESS_TYPE_DAEMON
        self.check_if_root()
        argv_left = self.parse_args(argv, argc)
        self.parse_argv_left(argv_left)
        setup_logging()
        self.read_config()
        reconfigure_logging()
        self.daemonize()
        setup_file_logging()
        self.init_signals()
        self.main_process()



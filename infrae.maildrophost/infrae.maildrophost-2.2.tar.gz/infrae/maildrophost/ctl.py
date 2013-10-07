# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: ctl.py 51089 2013-10-07 11:51:02Z sylvain $

import atexit
import os
import signal
import subprocess
import sys
import psutil

from maildrop import write_pid, exit_function, handle_sigterm
from stringparse import parse_assignments
from stringparse import ParserSyntaxError

SCRIPT = os.path.join(os.path.dirname(__file__), 'maildrop.py')


def is_process_running(pid):
    """Return if a process with a given PID is actually running
    """
    try:
        p = psutil.Process(pid)
        return p.is_running()
    except (psutil.NoSuchProcess, ValueError):
        return False


def maildrop_pid(pidfile):
    """Return the PID in pidfile if any
    """
    try:
        with open(pidfile) as pf:
            pid = int(pf.read())
            return pid
    ## file errors
    except IOError:
        print>>sys.stdout, 'No pidfile found.'
    except ValueError:
        print>>sys.stdout, 'Invalid pidfile, file will be deleted.'
        ## remove pidfile
        try:
            os.unlink(pidfile)
        except OSError:
            ## pidfile could have already been deleted, be silent.
            pass
    return -1


def maildrop_start(configuration, pidfile):
    """Start maildrophost.
    """
    if not os.path.isfile(SCRIPT):
        print>>sys.stderr, 'Could not find MaildropHost server script.'
        sys.exit(1)

    if not os.path.isfile(configuration):
        print>>sys.stderr, 'Could not find MaildropHost configuration.'
        sys.exit(1)

    ## if there's no running process then start one
    pid = maildrop_pid(pidfile)
    if not is_process_running(pid):
        psutil.Popen([sys.executable, SCRIPT, configuration])
        print>>sys.stdout, 'MaildropHost STARTED.'
    else:
        print>>sys.stderr, 'MaildropHost is already running with PID %s.' % pid
        sys.exit(1)


def maildrop_fg(configuration, pidfile):
    """Start maildrophost in the foreground.

    If you use this *and* you set DEBUG or SUPERVISED_DAEMON to a true
    value, it should be a fine configuration to use with supervisor.
    """
    if not os.path.isfile(SCRIPT):
        print>>sys.stderr, 'Could not find MaildropHost server script.'
        sys.exit(1)

    if not os.path.isfile(configuration):
        print>>sys.stderr, 'Could not find MaildropHost configuration.'
        sys.exit(1)

    ## if there's no running process then start one
    pid = maildrop_pid(pidfile)
    if not is_process_running(pid):
        print>>sys.stdout, 'Starting MaildropHost...'
        # We will not fork, so write the pid of the current script in
        # the pidfile.

        try:
            config = dict(parse_assignments(open(configuration).read()))
        except ParserSyntaxError:
            print>>sys.stderr, 'Cannot load config from "%s"' % configuration
            sys.exit(1)
        if not config['SUPERVISED_DAEMON']:
            print>>sys.stderr, (
                'When running in foreground mode SUPERVISED_DAEMON '
                'must be turned on in the configuration file at "%s"' %
                configuration)
            sys.exit(1)

        write_pid(pidfile, os.getpid())
        atexit.register(exit_function, pidfile)
        signal.signal(signal.SIGTERM, handle_sigterm)
        subprocess.call([sys.executable, SCRIPT, configuration])
    else:
        print>>sys.stderr, 'MaildropHost is already running with PID %s.' % pid
        sys.exit(1)


def maildrop_stop(configuration, pidfile):
    """Stop maildrophost.
    """
    pid = maildrop_pid(pidfile)
    try:
        p = psutil.Process(pid)
    except (psutil.NoSuchProcess, ValueError):
        print>>sys.stderr, 'MaildropHost is probably NOT running.'
        sys.exit(1)
    p.terminate()
    print>>sys.stdout, 'MaildropHost STOPPED.'
    try:
        p.wait(2)
    except psutil.TimeoutExpired:
        print>>sys.stdout, 'Termination timed out, process will be killed.'
        p.kill()
        print>>sys.stdout, 'MaildropHost KILLED.'
    ## remove pidfile
    try:
        os.unlink(pidfile)
    except OSError:
        ## pidfile could have already been deleted, be silent.
        pass


def maildrop_status(configuration, pidfile):
    """Look after the MaildropHost process status.
    """
    pid = maildrop_pid(pidfile)
    if is_process_running(pid):
        print>>sys.stdout, 'MaildropHost is running with PID %s' % pid
    else:
        print>>sys.stderr, 'MaildropHost is probably NOT running.'
        sys.exit(1)


def usage():
    print "usage: %s [start|fg|stop|restart|status]" % sys.argv[0]
    sys.exit(-255)


def main(options):
    if len(sys.argv) != 2:
        return usage()
    action = sys.argv[1]
    if action == 'start':
        return maildrop_start(**options)
    elif action == 'fg':
        return maildrop_fg(**options)
    elif action == 'stop':
        return maildrop_stop(**options)
    elif action == 'restart':
        maildrop_stop(**options)
        return maildrop_start(**options)
    elif action == 'status':
        return maildrop_status(**options)
    return usage()

# -*- coding: utf-8 -*-
# Copyright (c) 2007-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: ctl.py 33526 2009-02-13 11:11:59Z sylvain $

import os, signal, sys

def maildrop_start(config):
    """Start maildrophost.
    """
    mconfig = os.path.join(config['base'], 'config.py')
    if not os.path.isfile(mconfig):
        # probably using maildrophost >= 1.22
        mconfig = os.path.join(config['base'], 'config')

    mscript = os.path.sep.join(('maildrop', 'maildrop.py'))
    mscript = os.path.join(config['base'], mscript)
    os.execlp(sys.executable, sys.executable, mscript, mconfig)

def maildrop_stop(config):
    """Stop maildrophost.
    """
    if not os.access(config['pidfile'], os.R_OK):
        print "Can't find PID file. Daemon probably not running."
        return 1
    pid = int(open(config['pidfile']).read())
    os.kill(pid, signal.SIGTERM)
    os.unlink(config['pidfile'])
    print 'Stop %d daemon.' % pid
    return 0


def main(config, action=None):
    if action:
        if action[0] == 'start':
            return maildrop_start(config)
        elif action[0] == 'stop':
            return maildrop_stop(config)
        elif action[0] == 'restart':
            maildrop_stop(config)
            return maildrop_start(config)
    print "usage: %s [start|stop|restart]" % sys.argv[0]
    return 1




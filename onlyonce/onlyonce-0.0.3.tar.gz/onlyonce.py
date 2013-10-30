#!/usr/bin/env python
'''
    ---------
    Only Once
    ---------
    A simple Lock Dir system. Creating Dirs is atomic, which is useful for
    locking things to only let one version of a process start.

    ------
    Usage:
    ------
    try:
        with onlyonce.SingleProcessLock('/tmp/lock') as lock:
            lock.run('rsync', '-avz', '/here', 'there')
    except onlyonce.StillRunning as err:
        print str(err)


'''

__version__ = '0.0.3'

from subprocess import Popen, CalledProcessError, PIPE
import signal
from datetime import datetime
from os.path import join as pathjoin
from os import remove, mkdir, stat
from shutil import rmtree
from time import sleep, time


##############
# Exceptions #
##############

class StillRunning(Exception):
    ''' Process is still running Exception '''
    def __init__(self, pid):
        self.pid = pid
    def __str__(self):
        return 'Process is still running!({0})'.format(self.pid)


##########################
# Small useful functions #
##########################

__PROCESSES__ = []
__SIGHANDLER__ = signal.SIG_DFL

def sighandler(num, stack): # pylint: disable=W0613
    ''' when things go pear-shaped '''
    for lock in __PROCESSES__:
        lock.terminate_please()

        try:
            rmtree(lock.dirname)
        except OSError:
            # OK. Already done.
            pass

    if __SIGHANDLER__ != signal.SIG_DFL:
        __SIGHANDLER__(num, stack)

    exit(1)

def register_for_sighandler(singleprocesslock):
    ''' register a singleprocesslock with the module global sighandler
        function, to be cleared up if this python task is asked to quit. '''

    global __SIGHANDLER__, __PROCESSES__

    # What's currently handling things?
    current_handler = signal.getsignal(signal.SIGTERM)

    # If it's not us, and not the default, then log what it is, so we can
    # hand over to it after clearing up our mess.
    if current_handler != signal.SIG_IGN and current_handler != sighandler:
        __SIGHANDLER__ = current_handler

    signal.signal(signal.SIGTERM, sighandler)

    __PROCESSES__.append(singleprocesslock)

def deregister_on_sighandler(singleprocesslock):
    ''' remove a processlock from the list to be cleaned up
        if the process is killed, and if there are none left, then set
        the signal handler back to what it was before '''

    global __SIGHANDLER__, __PROCESSES__

    __PROCESSES__.remove(singleprocesslock)

    if len(__PROCESSES__) == 0:
        signal.signal(signal.SIGTERM, __SIGHANDLER__)

def age_of_file(filename):
    ''' how long since a file/folder was modified? '''
    return time() - stat(filename).st_mtime


def running_pid_from_file(filename):
    ''' tries to open a pidfile, and tell you if the process identified
        by it's contents is still running. '''
    try:
        pid = open(filename).read(1000).strip()
    except IOError:
        return False

    ps = Popen(['ps', '-p', pid], stderr=PIPE, stdout=PIPE )
    ps.communicate()

    if ps.returncode:
        return False
    else:
        return int(pid)


def note(text, level='INFO'):
    ''' print the date, level, and message '''
    now = str(datetime.now())
    print '{0}:{1}:{2}'.format(level, now, text)


####################################
# The main SingleProcessLock class #
####################################


class SingleProcessLock(object): #pylint: disable=R0903
    ''' a very simple atomic file lock, with some level of process awareness '''
    process = None

    def __init__(self, dirname):
        self.dirname = dirname
        self.pidfile = pathjoin(dirname, 'PID')

    def __enter__(self):
        ''' aquire the lockdir, if we can. if it already exists, check that the
            process that aquired it is still running, and if it is, raise
            StillRunning, otherwise, delete the pidfile, and note that the
            former process seems to have died '''

        try:
            mkdir(self.dirname)
        except OSError:
            # OK, dir already exists. Is the process running?
            pid = self.running()
            if pid:
                raise StillRunning(pid)
            else:
                # OK. It seems to have died, but not cleaned up after
                # itself.  This isn't great, but oh well.
                note('Previously seems to have failed.', 'WARNING')
                try:
                    remove(self.pidfile)
                except OSError:
                    # seems like it's gone already
                    pass

        register_for_sighandler(self)
        return self


    def write_pid(self, pid):
        ''' write the pid to the pidfile '''
        with open(self.pidfile, 'w') as pidfile:
            pidfile.write(str(pid))

    def running(self):
        ''' is the current process running still? '''
        first = running_pid_from_file(self.pidfile)
        if first:
            return first
        else:
            # there is a dir, but no pid running. So check how long since
            # the dir was last edited, and if it's really recent, then wait
            # a second and try again:
            try:
                if age_of_file(self.dirname) < 2:
                    # and wait a sec for race conditions...
                    sleep(1)
                    return running_pid_from_file(self.pidfile)
            except OSError:
                # OK, fine.  Looks like there is no process running now.
                return False



    def __exit__(self, exptype, expvalue, exptb):
        ''' clean up after yourself! (raises StillRunning
            if the process is still running) '''
        pid = self.running()

        if pid:
            if exptype:
                self.terminate_please()
            else:
                raise StillRunning(pid)
        else:
            try:
                rmtree(self.dirname)
            except OSError:
                # hm. can't remove it, so it's already gone. Are we already in
                # exception handling mode?
                pass
            deregister_on_sighandler(self)

    def run(self, *vargs, **kwargs):
        ''' run a command, and write the pid to the file '''
        try:
            self.process = Popen(*vargs, **kwargs)
            self.write_pid(self.process.pid)
            self.process.wait()
        except KeyboardInterrupt:
            self.terminate_please()
            return False

    def terminate_please(self):
        ''' stop a child process from running. '''
        # ask it to stop:
        self.process.terminate()

        # give it a chance to comply:
        sleep(0.2)

        # did it listen to us?
        self.process.poll()
        if self.process.returncode == None:
            # fine! it doesn't listen, it doesn't live!
            self.process.kill()

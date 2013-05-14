import os
import subprocess
import threading
import logging
import signal
import errno
import time
import logging
from functools import wraps


logger = logging.getLogger(__name__)


class ProcessTimoutError(Exception): pass


class Popen(object):

    ANNIHILATE_TRIES = 30
    ANNIHILATE_PAUSE = 1.0

    def timeoutcall(f):

        @wraps(f)
        def _w(self, *args, **kwargs):
            res = f(self, *args, **kwargs)
            if self.timeout is not None:
                for _ in xrange(self.ANNIHILATE_TRIES):
                    time.sleep(self.ANNIHILATE_PAUSE * 1.1)
                    self.check_for_timeout()
                    if self.poll() is not None:
                        break

            return res

        _w._timeoutcall = True
        return _w


    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop("timeout", None)
        self.logger = kwargs.pop("logger", logger)
        self.timed_out = False
        self.p = subprocess.Popen(*args, **kwargs)
        if self.timeout is not None:
            self.timeout_timer = threading.Timer(self.timeout, self.kill_after_timeout)
            self.timeout_timer.start()



    @timeoutcall
    def communicate(self, *args, **kwargs):
        return self.p.communicate(*args, **kwargs)


    @timeoutcall
    def wait(self):
        return self.p.wait()


    def poll(self):
        return self.p.poll()


    def check_for_timeout(self):
        logger.debug("check_for_timeout")
        if self.timed_out:
            raise ProcessTimoutError


    def kill_after_timeout(self):
        if self.poll() is None:
            logger.debug("Killing after timeout")
            self.annihilate()
            self.timed_out = True
            logger.debug("timeout set")


    @property
    def pid(self):
        return self.p.pid


    def kill(self, kill_signal=signal.SIGTERM):
        self.logger.debug("killing PID:%i with %i", self.pid, kill_signal)
        try:
            os.kill(self.pid, kill_signal)
            return True
        except OSError, e:
            # this means the child has
            # terminated already.
            if e.errno != errno.ESRCH:
                raise
        return False


    def annihilate(self, tries=ANNIHILATE_TRIES, pause=ANNIHILATE_PAUSE):
        for _ in xrange(tries):
            self.kill()
            time.sleep(pause)
            rc = self.poll()
            if rc is not None:
                return rc

        self.kill(signal.SIGKILL)
        while True:
            rc = self.poll()
            if rc is not None:
                break
            time.sleep(.1)

        return rc


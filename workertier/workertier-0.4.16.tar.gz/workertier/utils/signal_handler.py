#coding:utf-8
import signal

import gevent


def find_signum(name_or_signum):
    try:
        signum = int(name_or_signum)
    except ValueError:
        signum = getattr(signal, name_or_signum)
    return signum


class SignalHandler(object):
    """
    A delegate to receive signals and execute callbacks.

    "Superior" to gevent's signal because we can detach it, and can pass it a name or a number
    """

    #TODO: There is a circular reference between signal handler and callback here.

    def __init__(self, signum, callback):
        self.signum = signum
        self.callback = callback

        self.active = True
        gevent.signal(self.signum, self.on_signal)

    def on_signal(self):
        """
        Handle an incoming signal
        Runs synchronously: gevent already spawns a greenlet for us.
        """
        if self.active:
            self.callback()

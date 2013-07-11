#!/usr/bin/env python3
"""
Module THREADWRAPPER -- Child Thread Wrapper Object
Sub-Package STDLIB.COMM of Package PLIB3 -- General Python Utilities
Copyright (C) 2008-2013 by Peter A. Donis

This module contains the ``ThreadWrapper`` class, which provides
a portable interface to child threads and their exit status.
This class is used by the specialized threading functions in this
library.
"""

import threading

from ._childwrapper import ChildWrapper


class ChildThread(threading.Thread):
    # Fortunately we don't have to go through the same gymnastics
    # as for child processes (see the _processwrapper module)
    
    def run(self):
        # Python 3 threads make the internal variables visible to
        # subclasses, so we can just override this method to set
        # the exit code
        try:
            if self._target:
                self.exitcode = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs


class ThreadWrapper(ChildWrapper):
    
    thread_class = ChildThread
    
    thread = None
    
    def start(self):
        if self.thread is None:
            self.thread = self.thread_class(
                target=self._target, args=self._args, kwargs=self._kwargs)
            self.thread.daemon = self.shutdown_with_parent
            self.thread.start()
        else:
            raise RuntimeError("Thread already started.")
    
    def stop(self):
        # No way to stop a thread by default; this method can be overridden
        # to allow interaction with the thread via events or other means (in
        # such cases the thread_class class field can also be overridden to
        # use a subclass of ChildThread)
        pass
    
    def check(self):
        if self.thread is None:
            return True
        if not self.thread.is_alive():
            self._exitcode = self.thread.exitcode
            self.thread = None
            return True
        return False
    
    def wait(self):
        self.thread.join()
        self._exitcode = self.thread.exitcode
        self.thread = None

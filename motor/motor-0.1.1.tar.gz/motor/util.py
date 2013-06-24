# Copyright 2013 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A version of PyMongo's thread_util for Motor."""


import weakref
try:
    from time import monotonic as _time
except ImportError:
    from time import time as _time

import greenlet


class MotorGreenletIdent(object):
    def __init__(self):
        self._refs = {}

    def watching(self):
        """Is the current thread or greenlet being watched for death?"""
        return self.get() in self._refs

    def unwatch(self, tid):
        self._refs.pop(tid, None)

    def get(self):
        """An id for this greenlet"""
        return id(greenlet.getcurrent())

    def watch(self, callback):
        """Run callback when this greenlet dies.

        callback takes one meaningless argument.
        """
        current = greenlet.getcurrent()
        tid = self.get()

        if hasattr(current, 'link'):
            # This is a Gevent Greenlet (capital G), which inherits from
            # greenlet and provides a 'link' method to detect when the
            # Greenlet exits.
            current.link(callback)
            self._refs[tid] = None
        else:
            # This is a non-Gevent greenlet (small g), or it's the main
            # greenlet.
            self._refs[tid] = weakref.ref(current, callback)


class MotorGreenletCounter(object):
    """A greenlet-local counter.
    """
    def __init__(self):
        self.ident = MotorGreenletIdent()
        self._counters = {}

    def inc(self):
        # Copy these references so on_thread_died needn't close over self
        ident = self.ident
        _counters = self._counters

        tid = ident.get()
        _counters.setdefault(tid, 0)
        _counters[tid] += 1

        if not ident.watching():
            # Before the tid is possibly reused, remove it from _counters
            def on_thread_died(ref):
                ident.unwatch(tid)
                _counters.pop(tid, None)

            ident.watch(on_thread_died)

        return _counters[tid]

    def dec(self):
        tid = self.ident.get()
        if self._counters.get(tid, 0) > 0:
            self._counters[tid] -= 1
            return self._counters[tid]
        else:
            return 0

    def get(self):
        return self._counters.get(self.ident.get(), 0)


class ExceededMaxWaiters(Exception):
    pass


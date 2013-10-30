#!/usr/bin/python
#
# Copyright (c) 2013, Alon Bar-Lev <alonbl@redhat.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#


import threading
import weakref
import gc


class Destroyer(weakref.ref):

    _lock = threading.Lock()
    _refs = []

    def __new__(clz, instance=None, *args, **kwargs):
        return weakref.ref.__new__(clz, instance, clz._callback)

    def __init__(self, cls, instance, data):
        super(Destroyer, self).__init__(instance, self._callback)
        self._callback = cls.__destructor__
        self._data = data
        with self.__class__._lock:
            self.__class__._refs.append(self)

    @staticmethod
    def _callback(ref):
        ref._callback(ref._data)
        with ref.__class__._lock:
            ref.__class__._refs.remove(ref)


class O1(object):

    def __init__(self):
        print('O1::__init__ %s' % id(self))
        Destroyer(
            cls=O1,
            instance=self,
            data=id(self),
        )

    @staticmethod
    def __destructor__(data):
        print('O1::__destructor__ %s' % data)


class O2(O1):

    def __init__(self, o3):
        self.o3 = o3
        print('O2::__init__ %s' % id(self))
        # super(O2, self).__init__()
        Destroyer(
            cls=O2,
            instance=self,
            data=id(self),
        )

    @staticmethod
    def __destructor__(data):
        print('O2::__destructor__ %s' % data)


class O3(object):

    def __init__(self):
        self.o2 = O2(self)
        print('O3::__init__ %s' % id(self))
        Destroyer(
            cls=O3,
            instance=self,
            data=id(self),
        )

    @staticmethod
    def __destructor__(data):
        print('O3::__destructor__ %s' % data)


def main():
#     o2 = O2(O3())
    o3 = O3()

    # create cyclic reference
    # __del__ is not call at this
    # state
#     o2.x = o3
#     o3.x = o2


if __name__ == '__main__':
    try:
        main()
    finally:
        pass
        # gc.collect()


# vim: expandtab tabstop=4 shiftwidth=4

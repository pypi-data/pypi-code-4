# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 by Vicious Red Beam
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from memcacheliked import Memcacheliked, retrieval_command, storage_command, deletion_command, STORAGE_STATUS_STORED, DELETION_STATUS_DELETED, DELETION_STATUS_NOT_FOUND


class SampleServer(Memcacheliked):
    def __init__(self):
        Memcacheliked.__init__(self)
        self.data = {}
        self.flags = {}

    @retrieval_command
    def command_get(self, command_name, *keys):
        print('getting keys <%s>' % (keys,))
        return [(k, self.flags.get(k), self.data.get(k)) for k in keys]

    @storage_command
    def command_set(self, command_name, key, flags, exptime, value, *opts):
        print('setting key <%s> to <%s>' % (key, value,))
        self.data[key] = value
        self.flags[key] = flags
        return STORAGE_STATUS_STORED

    @deletion_command
    def command_delete(self, command_name, key, *opts):
        print('deleting key <%s>' % (key,))
        if key not in self.data:
            return DELETION_STATUS_NOT_FOUND
        del self.data[key]
        del self.flags[key]
        return DELETION_STATUS_DELETED


if __name__ == "__main__":
    SampleServer().start()

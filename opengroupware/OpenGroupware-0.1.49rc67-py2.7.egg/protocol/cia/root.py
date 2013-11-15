#
# Copyright (c) 2009, 2010, 2011, 2012. 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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
#
from coils.core import CoilsException
from coils.net import Protocol
from api import CIAAPI


class API(Protocol):
    __pattern__   = ['^RPC2$', 'cia', ]
    __namespace__ = 'cia'
    __xmlrpc__    = True

    def __init__(self, context):
        self.context = context
        self.api = CIAAPI(self.context)

    def get_name(self):
        return 'cia'

    def do_GET(self):
        raise CoilsException('XML-RPC calls must be POST commands')

    def getMaterializedRights(self, context_id, target_id):
        result = self.api.get_rights(context_id, target_id)
        return result

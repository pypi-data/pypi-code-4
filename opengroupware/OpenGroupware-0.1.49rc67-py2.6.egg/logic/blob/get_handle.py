#
# Copyright (c) 2010, 2012
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
import os
from coils.core import \
    Project,\
    Document, \
    CoilsException, \
    AccessForbiddenException, \
    Command
from coils.core.logic import GetCommand
from command import BLOBCommand


class GetDocumentHandle(Command, BLOBCommand):
    __domain__ = "document"
    __operation__ = "get-handle"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self.obj = params.get('document', None)
        if not self.obj:
            self.obj = params.get('object', None)
        if not self.obj:
            if 'id' in params:
                self.obj = self._ctx.run_command('document::get',
                                                 id=params['id'], )
            elif 'object_ids' in params:
                self.obj = self._ctx.run_command('document::get',
                                                 id=params['object_ids'][0], )
        if not self.obj:
            raise CoilsException(
                'No document specified for document::get-handle')

        self._mode = params.get('mode', 'rb')
        self._encoding = params.get('encoding', 'binary')
        self._version = params.get('version', None)

    def check_run_permissions(self):
        rights = self._ctx.access_manager.access_rights(self.obj, )
        if not set('rw').intersection(rights):
            raise AccessForbiddenException(
                'Insufficient access to {0}'.format(self.obj, ))

    def run(self, **params):
        filename = None
        db = self._ctx.db_session()
        # Failure to marshall a BLOBManager will raise an exception on its own
        manager = self.get_manager(self.obj)
        if manager:
            self._result = self.get_handle(
                manager,
                self._mode,
                self.obj,
                version=self._version,
                encoding=self._encoding,
            )
        else:
            self._result = None

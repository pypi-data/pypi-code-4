#
# Copyright (c) 2011, 2012, 2013
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
#
from coils.core import AccessForbiddenException, CoilsException
from coils.core.logic import DeleteCommand
from command import BLOBCommand


class DeleteDocumentVersion(DeleteCommand, BLOBCommand):
    __domain__ = "document"
    __operation__ = "delete-version"

    def __init__(self):
        DeleteCommand.__init__(self)

    def parse_parameters(self, **params):
        if 'document' in params:
            self._document = params['document']
        elif 'id' in params:
            self._document = self._ctx.run_command('document::get',
                                                   id=long(params['id']), )
        else:
            raise CoilsException(
                'No document specified for document::delete-version')

        self._version = int(params.get('version', 1))

    def check_run_permissions(self):
        rights = self._ctx.access_manager.access_rights(self._document)
        if not set('wadt').intersection(rights):
            raise AccessForbiddenException(
                'Insufficient access to {0}'.format(self._document, ))

    def run(self):
        '''
        WARNING: This deletes the BLOB [by calling delete_version] but the
        database transaction could still rollback!!! We have to delete the
        BLOB first as we cannot visualize the path to the BLOB once the
        ORM object is gone - we need a delete_on_commit and two phased
        deletion support.
        '''

        self.obj = self._ctx.run_command('document::get-version',
                                         document=self._document,
                                         version=self._version, )

        if self.obj:
            self.object_id = self.obj.object_id
            manager = self.get_manager(self._document)
            self.delete_version(manager, self._document, version=self._version)
            DeleteCommand.run(self)
            self._ctx.db_session().flush()
            self._ctx.db_session().refresh(self._document)

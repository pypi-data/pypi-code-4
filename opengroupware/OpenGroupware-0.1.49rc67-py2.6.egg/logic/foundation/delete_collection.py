#
# Copyright (c) 2010, 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core.logic import DeleteCommand


class DeleteCollection(DeleteCommand):
    __domain__ = "collection"
    __operation__ = "delete"

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('collection::get',
                                     id=object_id,
                                     access_check=access_check, )

    def check_run_permissions(self):
        rights = self._ctx.access_manager.access_rights(self.obj)
        if not set('wad').intersection(rights):
            raise AccessForbiddenException(
                'Insufficient access to {0}'.format(self.obj, ))

    def run(self):

        for assignment in self.obj.assignments:
            self._ctx.audit_at_commit(
                object_id=assignment.assigned_id,
                action='10_commented',
                message='Document removed from collection OGo#{0} "{1}" due '
                        'to collection deletion by OGo#{2} "{3}"'.
                        format(self.obj.object_id,
                               self.obj.title,
                               self._ctx.account_id,
                               self._ctx.login, ), )
            self._ctx.db_session().delete(assignment)

        DeleteCommand.run(self)

#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import \
    CoilsException, \
    AccessForbiddenException, \
    Command, \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_DATA_MANAGER

from command import BLOBCommand


class CopyDocument(Command, BLOBCommand):
    __domain__ = "document"
    __operation__ = "copy"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self.obj = params.get('document', None)
        self.filename = params.get('to_filename', None)
        self.folder = params.get('to_folder', None)
        if not self.folder:
            raise CoilsException('Target folder is required for document copy')

        self.copy_props = params.get('copy_properties', False)
        self.copy_links = params.get('copy_links', False)
        self.copy_owner = params.get('retain_ownership', False)

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('document::get',
                                     id=object_id,
                                     access_check=access_check, )

    def check_run_permissions(self):
        rights = self._ctx.access_manager.access_rights(self.obj)
        if not set('ar').intersection(rights):
            raise AccessForbiddenException(
                'Insufficient access to {0}'.format(self.obj, ))
        rights = self._ctx.access_manager.access_rights(self.folder)
        if not set('aiw').intersection(rights):
            raise AccessForbiddenException(
                'Insufficient access to {0}'.format(self.folder, ))

    def audit_action(self):
        '''
        Record creation as copy in audit log
        '''

        self._ctx.audit_at_commit(
            object_id=self.obj.object_id,
            action='10_commented',
            message='Created as copy of OGo#{0} by "{1}"'.
                    format(self.origin.object_id,
                           self._ctx.get_login(), ))

        self._ctx.audit_at_commit(
            object_id=self.origin.object_id,
            action='10_commented',
            message='Copy OGo#{0} created by "{1}"'.
                    format(self.obj.object_id,
                           self._ctx.get_login(), ))

    def run(self):

        if not self.filename:
            self.filename = self.obj.get_file_name()

        rfile = self._ctx.run_command('document::get-handle',
                                      document=self.obj, )
        if not rfile:
            raise CoilsException(
                'Unable to marshall contents of origin document OGo#{0}'.
                format(self.obj.object_id, ))

        document_copy = self._ctx.run_command('document::new',
                                              folder=self.folder,
                                              name=self.filename,
                                              handle=rfile,
                                              values={}, )

        if self.copy_props:
            for prop in self._ctx.pm.get_properties(self.obj):
                self._ctx.property_manager.set_property(
                    entity=document_copy,
                    namespace=prop.namespace,
                    attribute=prop.name,
                    value=prop.get_value(), )

        if self.copy_links:
            self._ctx.link_manager.copy_links(self.obj, document_copy)

        if (
            self.copy_owner and
            (self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN) or
             self._ctx.has_role(OGO_ROLE_DATA_MANAGER))
        ):
            document_copy.owner_id = self.obj.owner_id

        self._ctx.link_manager.link(
            document_copy,
            self.obj,
            kind='coils:copyFrom',
            label='Origin Document OGo#{0}'.format(self.obj.object_id), )

        self.origin = self.obj
        self.obj = document_copy

        self.set_result(self.obj)

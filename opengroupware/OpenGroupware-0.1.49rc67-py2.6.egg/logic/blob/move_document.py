#
# Copyright (c) 2011, 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core          import *
from coils.foundation    import *
from command             import BLOBCommand

class MoveDocument(SetCommand, BLOBCommand):
    __domain__ = "document"
    __operation__ = "move"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        SetCommand.parse_parameters(self, **params)
        self.obj = params.get('document', None)
        self.filename = params.get('to_filename', None)
        self.folder = params.get('to_folder', None)

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('document::get', id=object_id,
                                                      access_check=access_check)


    def check_run_permissions(self):
        rights = self._ctx.access_manager.access_rights( self.obj, )
        if not set( 'aidt' ).intersection( rights ):
            raise AccessForbiddenException( 'Insufficient access to {0}'.format( self.obj ) )

    def audit_action(self):
        '''
        Record move and or re-name in the entity audit log.
        '''

        message = 'Document'
        if self.previous_folder_id:
            message += ' moved from folder OGo#{0} to OGo#{1}'.format( self.previous_folder_id, self.obj.folder_id )
            if self.filename:
                message += ';renamed to "{0}"'.format( self.filename )
        elif self.filename:
            message += ' renamed to "{0}"'.format( self.filename )

        self._ctx.audit_at_commit( object_id = self.obj.object_id,
                                   action    = '05_changed',
                                   message   = message )

    def run(self):

        self.previous_folder_id = None

        # TODO: Check write support on target folder
        if self.obj.folder_id != self.folder.object_id:
            # The *FOLDER* the document is in has changed as a result of the move
            if self.obj.project_id != self.folder.project_id:
                # TODO: Can documents be *MOVED* between projects?
                #   Projects may have radically different backends and historical
                #   document versions will still need to be 'findable'. Between
                #   projects should be a copy or at worse a copy-and-delete-source.
                # WARN: For now we are refusing this action!
                raise NotImplementedException('Documents cannot be moved between projects')
                self.document.project_id = self.folder.project_id
                if self.folder.project:
                    self.increment_object_version(self.folder.project)
            self.previous_folder_id = self.obj.folder_id
            self.obj.folder_id   = self.folder.object_id
            # Bump folder properties
            self.folder.modified = self._ctx.get_utctime()
            self.increment_object_version(self.obj.folder)
            self.folder.status   = 'updated'

        old_extension = self.obj.extension
        if self.filename:
            # Filename as well as location has changed

            filename = self.filename.split('.')

            if (len(filename) > 1):
                self.obj.extension = filename[-1]
                self.obj.name      = '.'.join(filename[:-1])
            else:
                self.obj.extension = None
                self.obj.name = self.filename

            self.change_extension( self.obj, old_extension )


        self.increment_version()

        # Move versions?  Deleting versions looks like, there is not Logic command currently
        # implemented to move versions of a document to a different project.
        # versions = self._ctx.run_command('document::get-versions', document=self.obj)
        # for version in versions:
        #     self._ctx.run_command('document::delete-version', document=self.obj
        self.set_result(self.obj)

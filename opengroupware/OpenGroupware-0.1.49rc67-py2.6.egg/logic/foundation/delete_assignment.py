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
from sqlalchemy          import *
from sqlalchemy.orm.exc  import NoResultFound
from coils.core          import *

class DeleteCollectionAssignment(Command):
    # TODO: Delete related collection assignments
    __domain__    = "collection"
    __operation__ = "delete-assignment"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.collection      = params.get( 'collection', None )
        if 'entity' in params:
            self.assigned_id = params.get( 'entity' ).object_id
        elif 'assigned_id' in params:
            self.assigned_id = long( params.get( 'assigned_id' ) )
        else:
            raise CoilException('Assignment to delete not specified as entity or assigned_id')

    def check_run_permissions(self):
        rights = self._ctx.access_manager.access_rights( self.collection, )
        if not set( 'wta' ).intersection( rights ):
            raise AccessForbiddenException( 'Insufficient access to {0}'.format( self.collection ) )

    def run(self):
        try:
            assignment = self._ctx.db_session( ).\
                         query( CollectionAssignment ).\
                         filter( and_( CollectionAssignment.collection_id == self.collection.object_id,
                                       CollectionAssignment.assigned_id   == self.assigned_id ) ).\
                         one ( )
        except NoResultFound:
            self.set_return_value( False )
            return

        # Delete the assignment
        self._ctx.db_session( ).delete( assignment )

        self._ctx.audit_at_commit( self.collection.object_id,
                                   '05_changed',
                                   'Removed OGo#{0} from collection.'.format( self.assigned_id, ) )

        self._ctx.audit_at_commit( self.assigned_id,
                                   '05_changed',
                                   'Removed from collection OGo#{0}'.format( self.collection.object_id, ) )

        self.set_return_value( True )

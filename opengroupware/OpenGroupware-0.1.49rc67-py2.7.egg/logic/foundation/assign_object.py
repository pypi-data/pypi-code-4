#
# Copyright (c) 2011, 2013
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
from sqlalchemy       import *
from sqlalchemy.orm.exc  import NoResultFound
from coils.core       import *
from keymap           import COILS_COLLECTION_ASSIGNMENT_KEYMAP

class AssignObject(Command):
    __domain__ = "object"
    __operation__ = "assign-to-collection"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self.collection  = params.get('collection', None)  ## The collection in question
        if not self.collection:
            raise CoilsException('No collection provided to set-assignment')

        self.assigned    = params.get('entity',     None)  ## Add these entities
        if not self.assigned:
            raise CoilsException('No entity provided to set-assignment to assign')

    def check_run_permissions(self):
        rights = self._ctx.access_manager.access_rights( self.collection, )
        if not set( 'wia' ).intersection( rights ):
            raise AccessForbiddenException( 'Insufficient access to {0}'.format( self.collection ) )

    def get_max_key(self):
        max_key = 0
        for assignment in self.collection.assignments:
            if (assignment.sort_key > max_key):
                max_key = assignment.sort_key
        return max_key

    def get_assignment(self):
        db = self._ctx.db_session()
        try:
            result = db.query( CollectionAssignment ).\
                     filter( and_( CollectionAssignment.collection_id == self.collection.object_id,
                                   CollectionAssignment.assigned_id == self.assigned.object_id ) ).\
                     one( )
        except NoResultFound:
            return
        return result

    def run(self):

        obj = self.get_assignment()

        self.set_return_value( self.collection )

        if obj:
            # The entity is already assigned to the collection, nothing to do
            return

        db = self._ctx.db_session()

        obj = CollectionAssignment()
        obj.collection_id = self.collection.object_id
        obj.assigned_id   = self.assigned.object_id
        obj.sort_key      = self.get_max_key() + 1
        obj.entity_name   = self.assigned.__entityName__
        self._ctx.db_session( ).add( obj )

        self.collection.version += 1

        self._ctx.audit_at_commit( self.collection.object_id,
                                   '05_changed',
                                   'Assigned OGo#{0} to collection.'.format( self.assigned.object_id, ) )

        self._ctx.audit_at_commit( self.assigned.object_id,
                                   '05_changed',
                                   'Assigned to collection OGo#{0}'.format( self.collection.object_id, ) )

        return


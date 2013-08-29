#
# Copyright (c) 2013
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
import uuid, traceback, multiprocessing, json
from coils.core          import *

from events              import DOCUMENT_COLLECT_REQUEST,\
                                DOCUMENT_COLLECT_DISCARDED,\
                                DOCUMENT_COLLECT_FAILED,\
                                DOCUMENT_COLLECT_COMPLETED,\
                                DOCUMENT_DELETED

from utility             import NAMESPACE_MANAGEMENT,\
                                ATTRIBUTE_MANAGEMENT_COLLECTED,\
                                ATTRIBUTE_MANAGEMENT_COLLECTION_DESC,\
                                get_inherited_property,\
                                expand_labels_in_name


COMMAND_MAP = { DOCUMENT_COLLECT_REQUEST: 'auto_collect_document',
                DOCUMENT_DELETED:         'process_document_deletion', }

class EventWorker(MultiProcessWorker):

    def __init__(self, name, work_queue, event_queue, ):
        MultiProcessWorker.__init__( self, name, work_queue, event_queue )
        self.context = AdministrativeContext( )

    def process_worker_message(self, command, payload ):

        object_id = long( payload.get( 'objectId', 0 ) )

        if command in COMMAND_MAP:
            method = 'do_{0}'.format( COMMAND_MAP[ command ] )
            if hasattr( self, method ):
                method = getattr( self, method )
                if method:
                    method( object_id, )
            else:
                self.log.error( 'Command received with no corresponding implementation; looking for "{0}"'.format( method ) )
        else:
            self.log.error( 'Unmapped command "{0}" received.'.format( command ) )

    def do_auto_collect_document(self, object_id):

        document = self.context.run_command( 'document::get', id=object_id )
        if not document:
            self.enqueue_event( DOCUMENT_COLLECT_DISCARDED, ( object_id, 'Document', 'Document not available', ), )
            return

        prop = self.context.property_manager.get_property( document, NAMESPACE_MANAGEMENT, ATTRIBUTE_MANAGEMENT_COLLECTED )
        if prop:
            self.enqueue_event( DOCUMENT_COLLECT_DISCARDED, ( object_id, 'Document', 'Document already collected', ), )
            return

        collection_desc = get_inherited_property( self.context, document, NAMESPACE_MANAGEMENT, ATTRIBUTE_MANAGEMENT_COLLECTION_DESC )
        if not collection_desc:
            self.enqueue_event( DOCUMENT_COLLECT_DISCARDED, ( object_id, 'Document', 'No collection path defined.', ), )
            return

        try:
            collection_description = json.loads( collection_desc )
        except:
            self.enqueue_event( DOCUMENT_COLLECT_FAILED, ( object_id, 'Document', traceback.format_exc( ) ) )
            return
        else:
            collection_name = expand_labels_in_name( collection_description.get( 'name', None ) )
            if not collection_name:
                self.enqueue_event( DOCUMENT_COLLECT_FAILED, ( object_id, 'Document', 'Collection description has no name.' ) )
                return

            collection_description[ 'name' ] = collection_name

        criteria = [ { 'key':   'name', 'value': collection_description[ 'name' ] }, ]
        if collection_description.get( 'kind', None ):
            criteria.append( { 'key': 'kind', 'value': collection_description[ 'kind' ] }, )

        collection = self.context.run_command( 'collection::search', criteria=criteria )
        if not collection:
            collection = self.context.run_command( 'collection::new', values=collection_description )
            collection.project_id = document.project_id
            self.log.info( 'Automatically created new collection OGo#{0}'.format( collection.object_id ) )
        else:
            # Searches always have multiple results, we are taking the first one
            collection = collection[ 0 ]
            self.log.debug( 'Discovered OGo#{0} [Collection] that matches descriptor'.format( collection.object_id ) )

        self.context.run_command( 'object::assign-to-collection', collection=collection, entity=document )

        self.log.debug( 'OGo#{0} [Document] automatically joined to OGo#{1} [Collection]'.format( document.object_id, collection.object_id ) )

        self.context.property_manager.set_property( document, NAMESPACE_MANAGEMENT, ATTRIBUTE_MANAGEMENT_COLLECTED,
                                                    'OGo#{0};name:"{1}";kind:"{2}"'.format( collection.object_id,
                                                                                            collection_description[ 'name' ],
                                                                                            collection_description.get( 'kind', None ) ) )

        self.log.debug( 'OGo#{0} [Document] collection join recorded via property'.format( document.object_id, ) )

        self.context.commit( )

        self.log.debug( 'OGo#{0} [Document] collection join committed.'.format( document.object_id, ) )

        self.enqueue_event( DOCUMENT_COLLECT_COMPLETED, ( object_id, 'Document', None ) )

        return

    def process_document_deletion(self, object_id):

        # Collections

        # Object-Links

        return


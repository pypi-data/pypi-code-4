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
# THE  SOFTWARE.
#
import uuid, multiprocessing, Queue
from sqlalchemy       import and_
from coils.core       import *
from event_worker     import EventWorker

from events              import DOCUMENT_COLLECT_REQUEST,\
                                DOCUMENT_COLLECT_DISCARDED,\
                                DOCUMENT_COLLECT_FAILED,\
                                DOCUMENT_COLLECT_COMPLETED,\
                                DOCUMENT_DELETED

from utility          import get_inherited_property


COMMAND_MAP = { DOCUMENT_COLLECT_DISCARDED: None,
                DOCUMENT_COLLECT_FAILED:    'handle_collection_failed',
                DOCUMENT_COLLECT_COMPLETED: None, }

class EventService(ThreadedService):
    __service__ = 'coils.blob.event'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def worker_name_generator(self):
        return 'coils.blob.event.worker({0})'.format( uuid.uuid4().hex )

    def setup(self, silent=True):
        ThreadedService.setup( self, silent=silent )

        self._broker.subscribe( '{0}.notify'.format( self.__service__, ),
                                self.receive_message,
                                expiration=900000,
                                queue_type='fanout',
                                durable=False,
                                exchange_name='OpenGroupware_Coils_Notify' )

        self.start_workers( count=4, classname=EventWorker, name_generator=self.worker_name_generator )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext( { }, broker=self._broker )

    def process_service_specific_event(self, event_class, event_data):
        if event_class in COMMAND_MAP:
            method_name = COMMAND_MAP.get( event_class )
            if method_name:
                if hasattr( self, method_name ):
                    method = getattr( self, method_name )
                    tmp = method( event_data )
                else:
                    self.log.error( 'Method "{0}" mapped from event "{1}" does not exist.'.format( method_name, event_class ) )
            else:
                self.log.info( 'Event "{0}" mapped as  no-operation'.format( event_class ) )
        else:
            self.log.warn( 'Event "{0}" is not in command processing map'.format( event_class ) )

    #
    # Message Handlers
    #

    def do___audit_document(self, parameter, packet):

        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )

        try:
            if action_tag in ( '00_created', ):
                self.enqueue_work( DOCUMENT_COLLECT_REQUEST, packet.data )
            elif action_tag in ( '99_deleted', ):
                self.enqueue_work( DOCUMENT_DELETED, packet.data )
        except Queue.Full:
            self.log.info( 'Unable to queue document event for processing' )

        return


    #
    # Event handling
    #

    def handle_collection_failed(self, event_data ):
        pass


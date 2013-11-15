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
#
import uuid, multiprocessing, Queue
from sqlalchemy       import and_
from coils.core       import *
from thumbworker      import ThumbWorker

from events              import AUTOTHUMB_NAIL_REQUEST, \
                                AUTOTHUMB_NAIL_CREATED, \
                                AUTOTHUMB_NAIL_FAILED

from edition             import AUTOTHUMBNAILER_VERSION

class AutoThumbService(ThreadedService):
    __service__ = 'coils.blob.autothumb'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def worker_name_generator(self):
        return 'coils.blob.autothumb.worker({0})'.format( uuid.uuid4().hex )

    def setup(self, silent=True):
        ThreadedService.setup( self, silent=silent )

        self._broker.subscribe( '{0}.events'.format( self.__service__, ),
                                self.receive_message,
                                expiration=900000,
                                queue_type='fanout',
                                durable=False,
                                exchange_name='OpenGroupware_Coils_Notify' )

        self.start_workers( count=4, classname=ThumbWorker, name_generator=self.worker_name_generator )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext( { }, broker=self._broker )

    def process_service_specific_event(self, event_class, event_data):
        if event_class == AUTOTHUMB_NAIL_FAILED:
            object_id, entity_name, error_text, = event_data
            self.send_administrative_notice(
                subject='Thumbnailer encountered an error processing OGo#{0} [{1}]'.format( object_id, entity_name ),
                message=error_text,
                urgency=5,
                category='data' )
        elif event_class == AUTOTHUMB_NAIL_CREATED:
            pass

    #
    # Message Handlers
    #

    def do___audit_document(self, parameter, packet):

        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )

        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass

        #This some type of change, recalculate the thumbnail

        try:
            self.enqueue_work( AUTOTHUMB_NAIL_REQUEST, object_id )
        except Queue.Full:
            self.log.info( 'Unable to queue audit-document request' )

        # TODO: Delete any now expire thumbnails

    def do_process_since(self, parameter, packet):

        object_id = long( packet.data.get( 'objectId', 0 ) )

        db = self._ctx.db_session( )
        query = db.query( Document.object_id ).filter( Document.object_id > object_id )
        counter = 0
        for result in query.all( ):
            try:
                self.enqueue_work( AUTOTHUMB_NAIL_REQUEST, result[ 0 ] )
            except Queue.Full:
                self.log.info( 'Unable to queue entire unit-of-work for process-since request' )
                break

            counter += 1

        self.log.debug( 'Queued {0} documents for nailing as result of process-since request'.format( counter ) )

    def do_process_range(self, parameter, packet):

        start_object_id = long( packet.data.get( 'startObjectId', 0 ) )
        end_object_id = long( packet.data.get( 'endObjectId', 0 ) )

        db = self._ctx.db_session( )
        query = db.query( Document.object_id ).filter( and_( Document.object_id >= start_object_id,
                                                             Document.object_id <= end_object_id ) )
        counter = 0
        for result in query.all( ):

            try:
                self.enqueue_work( AUTOTHUMB_NAIL_REQUEST, result[ 0 ] )
            except Queue.Full:
                self.log.info( 'Unable to queue entire unit-of-work for process-range request' )
                break

            counter += 1

        self.log.debug( 'Queued {0} documents for nailing as result of process-range request'.format( counter ) )

    def do_thumbnail(self, parameter, packet):

        try:
            self.enqueue_work( AUTOTHUMB_NAIL_REQUEST, long( parameter ) )
        except Queue.Full:
            self.log.info( 'Unable to queue thumbnail request' )

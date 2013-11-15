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
import uuid, traceback, multiprocessing, sys, logging, Queue, time

EVENTQUEUE_MAX_SIZE=4096

from worker_events    import AMQ_RECEIVED, \
                             AMQ_TRANSMIT, \
                             AMQ_ACKNOWLEDGE, \
                             AMQ_FAIL, \
                             AMQ_TIMEOUT, \
                             WORKER_ERROR, \
                             SEND_ADMIN_NOTICE

class MultiProcessWorker(multiprocessing.Process):

    def __init__(self, name, work_queue, event_queue, ):
        multiprocessing.Process.__init__( self )
        self.name = name
        self.work_queue = work_queue
        self.event_queue = event_queue
        self.running = True
        self.log = logging.getLogger( self.name )

    def setup(self):
        sys.stdin  = open('/dev/null', 'r')
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')

    def enqueue_event(self, command, payload):
        try:
            self.event_queue.put((command, payload, ))
        except Queue.Full:
            while self.event_queue.full():
                self.log.debug(
                    'Waiting for available event queue space; {0} of {1}'.
                    format(self.event_queue.qsize(), EVENTQUEUE_MAX_SIZE, ))
                time.sleep(1.0)
            self.enqueue_event(command, payload)

    def run(self):
        self.setup( )
        try:
            import procname
            procname.setprocname( self.name )
        except:
            self.log.info('Failed to set process name for service')

        while self.running:
            self.log.debug( 'IDLE' )

            try:

                ( command, payload, target, ) = self.work_queue.get( )

                if target:
                    # This message is not for us, put it back in the queue
                    # TODO: What happens with messages sent to a worker that is defunct?
                    if target != self.name:
                        self.log.debug( 'Discard worker message - not mine, targeted to "{0}"'.format( target ) )
                        self.work_queue.put( ( command, payload, target, ) )
                        continue

                if command == None:
                    self.log.debug( 'Worker commencing self-termination due to NULL command' )
                    self.running = False
                else:
                    self.process_worker_message( command, payload )
            except KeyboardInterrupt:
                break
            except Exception, e:
                self.log.error( 'Unexpected exception in component worker "{0}"'.format( self.name ) )
                self.log.exception( e )
                message = 'Worker:{0}\n  Command: {1}\n  Payload: {2}\n  Target: {3}\n\n{4}\n'.\
                          format( self.name, command, payload, target, traceback.format_exc( ) )
                self.enqueue_event( WORKER_ERROR, message )

        self.context.close( )

    def process_worker_message(self, command, payload):
        self.log.error( 'WORKER SHOULD NOT BE HERE!')
        pass

    def send_administrative_notice(self, subject=None,
                                         message=None,
                                         urgency=9,
                                         category='unspecified'):
        self.enqueue_event(
            SEND_ADMIN_NOTICE,
            (subject,
             message,
             urgency,
             category, ), )

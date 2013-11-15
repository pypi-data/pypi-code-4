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
import uuid
import multiprocessing
import logging
import random
import Queue
from datetime import datetime, timedelta
from coils.core import \
    Packet, \
    ThreadedService, \
    ObjectInfo, \
    AuditEntry, \
    UniversalTimeZone, \
    AdministrativeContext
from orm import SearchVector
from sqlalchemy import func
from index_worker import VistaWorker
from events import \
    VISTA_VECTOR_REFRESHED, \
    VISTA_VECTOR_CURRENT, \
    VISTA_INVALID_ENTITY, \
    VISTA_VECTOR_ERROR_UNICODE, \
    VISTA_VECTOR_ERROR_ACCESS, \
    VISTA_VECTOR_ERROR_OTHER, \
    VISTA_UNSUPPORTED_ENTITY, \
    VISTA_MISSING_ENTITY, \
    VISTA_INDEX_REQUEST, \
    VISTA_VECTOR_ERROR_INTEGRITY, \
    VISTA_INDEX_EXPUNGE


EVENTQUEUE_MAX_SIZE = 4096


class IndexService (ThreadedService):
    __service__ = 'coils.vista.index'
    __auto_dispatch__ = True

    def __init__(self):
        self._floor = 0
        self.index_backlog = set()
        self.expunge_backlog = set()
        ThreadedService.__init__(self)

    def worker_name_generator(self):
        return 'coils.vista.worker({0})'.format(uuid.uuid4().hex, )

    def setup(self, silent=True):
        ThreadedService.setup(self, silent=silent, )
        self._broker.subscribe('{0}.events'.format(self.__service__, ),
                               self.receive_message,
                               expiration=900000,
                               queue_type='fanout',
                               durable=False,
                               exchange_name='OpenGroupware_Coils_Notify', )
        self.start_workers(
            count=10,
            classname=VistaWorker,
            name_generator=self.worker_name_generator, )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker, )
        self._backoff_queue = {}

    def process_service_specific_event(self, event_class, event_data):

        if event_class == VISTA_VECTOR_ERROR_UNICODE:
            object_id, entity_name, error_text, = event_data
            self.send_administrative_notice(
                subject='Unicode error encountered indexing OGo#{0} [{1}]'.
                        format(object_id, entity_name, ),
                message=error_text,
                urgency=5,
                category='data', )
        elif event_class == VISTA_VECTOR_ERROR_ACCESS:
            object_id, entity_name, error_text, = event_data
            self.send_administrative_notice(
                subject='Attribute access error indexing OGo#{0} [{1}]'.
                        format(object_id, entity_name, ),
                message=error_text,
                urgency=7,
                category='model', )
        elif event_class == VISTA_VECTOR_ERROR_OTHER:
            object_id, entity_name, error_text, = event_data
            self.send_administrative_notice(
                subject='A general exception while indexing OGo#{0} [{1}]'.
                        format(object_id, entity_name, ),
                message=error_text,
                urgency=9,
                category='vista', )
        elif event_class == VISTA_VECTOR_ERROR_INTEGRITY:
            object_id, entity_name, error_text, = event_data
            stamp = \
                datetime.now() + timedelta(seconds=random.randrange(5, 240))
            self.log.debug(
                'Placing reindex of OGo#{0} onto the backoff queue'.
                format(object_id, ))
            self._backoff_queue[stamp] = object_id
        elif event_class == VISTA_VECTOR_REFRESHED:
            # TODO: Log the refresh of the search vector?
            pass
        elif event_class == VISTA_VECTOR_CURRENT:
            pass
        elif event_class == VISTA_MISSING_ENTITY:
            pass
        elif event_class == VISTA_UNSUPPORTED_ENTITY:
            pass

        if self.expunge_backlog or self.index_backlog:
            self.drain_backlogs()

        return

    def drain_backlogs(self):

        if self.event_queue.full():
            return

        self.log.debug('Draining index expunge request backlog.')

        limit = min(
            (EVENTQUEUE_MAX_SIZE - self.event_queue.qsize()) - 1,
            len(self.expunge_backlog)
        )
        for _ in range(0, limit):
            self._expunge_index_entries(self.expunge_backlog.pop())

        if self.event_queue.full():
            return

        self.log.debug('Draining index update request backlog.')

        limit = min(
            (EVENTQUEUE_MAX_SIZE - self.event_queue.qsize()) - 1,
            len(self.index_backlog)
        )
        for _ in range(0, limit):
            self._create_entity_index(self.index_backlog.pop())

        return

    #
    # INDEXER Methods
    #

    def _create_entity_index(self, object_id):
        self.log.debug('Appending OGo#{0} to work queue'.format(object_id, ))
        try:
            self.enqueue_work(VISTA_INDEX_REQUEST, object_id, )
        except Queue.Full:
            self.index_backlog.add(object_id)
        except Exception as exc:
            self.log.error('Exception attempting to enqueue index request.')
            self.log.exception(exc)

    def _expunge_index_entries(self, object_id):
        self.log.debug(
            'Appending expunge of OGo#{0} to work queue'.format(object_id, ))
        try:
            self.enqueue_work(VISTA_INDEX_EXPUNGE, object_id, )
        except Queue.Full:
            self.expunge_backlog.add(object_id)
        except Exception as exc:
            self.log.error('Exception attempting to enqueue expunge request.')
            self.log.exception(exc)

    def _walk_backoff_queue(self):
        now = datetime.now()
        if self._backoff_queue:
            for stamp, object_id in self._backoff_queue.items():
                if stamp > now:
                    self._create_entity_index(object_id)
                    self.log.debug(
                        'Pushing reindex of OGo#{0} from backoff queue'.
                        format(object_id, ))
                    del self._backoff_queue.stamp[stamp]
    #
    # Message Handlers
    #

    def do_log_scan(self, parameter, packet):

        if self._floor:
            floor = self._floor
        else:
            floor = datetime.now() - timedelta(hours=72)
            floor = floor.replace(tzinfo=UniversalTimeZone())

        db = self._ctx.db_session()
        query = db.query(AuditEntry.context_id,
                         func.max(AuditEntry.datetime)).\
            filter(AuditEntry.datetime > floor).\
            group_by(AuditEntry.context_id)
        for record in query.all():
            object_id, event_time = record
            if event_time > floor:
                floor = event_time
            self._ctx.send(
                None,
                'coils.vista.index/index:{0}'.format(object_id, ),
                {}, )
        self._floor = floor

    def do_vacuum(self, parameter, packet):
        db = self._ctx.db_session()
        query = db.query(SearchVector.object_id).\
            outerjoin(
                ObjectInfo, ObjectInfo.object_id == SearchVector.object_id).\
            filter(ObjectInfo.object_id == None)
        result = query.all()
        count = len(result)
        self.log.debug('Purging {0} defunct search vectors.'.format(count))
        while result:
            chunk = result[: 100 if len(result) > 100 else len(result)]
            del result[: len(chunk)]
            db.query(SearchVector).\
                filter(SearchVector.object_id.in_(chunk)).\
                delete(synchronize_session=False)
            self._ctx.commit()
        self.log.debug('Search vector purge complete.')
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'Purge completed.', }
            )
        )

    def do_index(self, parameter, packet):

        try:
            object_id = long(parameter)
        except:
            self.send(
                Packet.Reply(
                    packet,
                    {'status': 500,
                     'text': 'Invald objectId specified.', }
                )
            )
            return

        self._create_entity_index(object_id)

    def do___audit_delete(self, parameter, packet):
        object_id = long(packet.data.get('objectId', 0))
        self._expunge_index_entries(object_id)

    def do___audit_contact(self, parameter, packet):
        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index(object_id)

    def do___audit_document(self, parameter, packet):
        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index(object_id)

    def do___audit_enterprise(self, parameter, packet):
        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index(object_id)

    def do___audit_note(self, parameter, packet):
        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index(object_id)

    def do___audit_project(self, parameter, packet):
        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index(object_id)

    def do___audit_task(self, parameter, packet):
        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index(object_id)

    def work(self):
        self._walk_backoff_queue()
        if self.expunge_backlog or self.index_backlog:
            self.drain_backlogs()

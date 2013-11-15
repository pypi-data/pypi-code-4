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
import select
import traceback
import psycopg2
import psycopg2.extensions
from sqlalchemy import and_, or_, func
from threading import Thread
from threading import local as thread_local
from coils.core import \
    ObjectInfo, \
    Packet, \
    ProcessLogEntry, \
    Lock, \
    Address, \
    Telephone, \
    ObjectProperty, \
    ProjectInfo, \
    DateInfo, \
    CompanyInfo, \
    Participant, \
    ProjectAssignment, \
    CompanyAssignment, \
    ObjectLink, \
    CollectionAssignment, \
    AuditEntry, \
    AdministrativeContext, \
    ServerDefaultsManager, \
    ThreadedService


EVENTQUEUE = 'auditEvent'

WATCHER_NAMESPACE = '817cf521c06b47228392a0437daf81e0'
WATCHER_TIMEOUT = 1000
WATCHER_NOTIFY = 1001
WATCHER_SHUTDOWN = 1002
WATCHED_TYPES = ['document', 'contact',     'enterprise', 'task',
                 'project',  'appointment', 'folder',     'note',
                 'route',    'process', ]

NOTIFY_EXCHANGE = 'OpenGroupware_Coils_Notify'


def watch_for_pgevents(service):

    def execute_listen(connection):
        cursor = connection.cursor()
        cursor.execute('LISTEN {0};'.format(EVENTQUEUE, ))
        return cursor

    event_queue = service.event_queue

    t = thread_local()
    t.ctx = AdministrativeContext()
    connection = \
        t.ctx.db_session().connection().connection.checkout().connection
    connection.set_isolation_level(
        psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = execute_listen(connection)
    restart_enabled = True
    while service.RUNNING and restart_enabled:
        try:
            if select.select([connection, ], [], [], 15) == ([], [], [], ):
                event_queue.put((WATCHER_TIMEOUT, None, ))
            else:
                connection.poll()
                while connection.notifies:
                    notify = connection.notifies.pop()
                    payload = notify.payload
                    event_queue.put((WATCHER_NOTIFY, None, ))
        except Exception as outer:
            t.ctx.log.exception(outer)
            service.send_administrative_notice(
                subject='An exception occured in the database event '
                        'watcher thread',
                message=traceback.format_exc(),
                urgency=8,
                category='service', )

            if restart_enabled:
                restart_enabled = False

                try:
                    cursor.close()
                    cursor = execute_listen(connection)
                except Exception as inner:
                    t.ctx.log.exception(inner)
                    service.send_administrative_notice(
                        subject='Failure to init database event watcher '
                                'cursor.',
                        message=traceback.format_exc(),
                        urgency=9,
                        category='service', )
                    event_queue.put((WATCHER_SHUTDOWN, None, ))
                else:
                    restart_enabled = True

    t.ctx.close()


class WatcherService (ThreadedService):
    __service__ = 'coils.watcher'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)
        self.create_auditor_thread()
        self.max_audit_entry = 0

    def create_auditor_thread(self, start=False):
        if 'audit' not in self.threads:
            self.threads['audit'] = Thread(target=watch_for_pgevents,
                                           name='pgListen',
                                           args=(self, ))
            audit_thread = self.threads['audit']
            if start:
                audit_thread.start()
                audit_thread.join(0.1)
        return self.threads['audit']

    def shutdown_auditor_thread(self):
        auditor = self.threads.get('audit', None)
        if auditor:
            while auditor.is_alive():
                auditor.join(1.0)
                if auditor.is_alive():
                    self.send_administrative_notice(
                        subject='Terminated auditor thread not complete',
                        message='Terminated auditor thread not complete.\n'
                                'Component "coils.watcher" is potentially '
                                'hung.\n',
                        urgency=6,
                        category='service', )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker, )
        self._sd = ServerDefaultsManager()

        prop = self._ctx.property_manager.get_server_property(
            WATCHER_NAMESPACE,
            'maxAuditEntry')
        if prop:
            self.max_audit_entry = long(prop.get_value())
        else:
            self.max_audit_entry = self._ctx.db_session().\
                query(func.max(AuditEntry.object_id)).\
                one()[0]
            self.persist_max_audit_entry()
            self._ctx.commit()

    def process_service_specific_event(self, event_class, event_data):
        if event_class == WATCHER_TIMEOUT:
            pass
        elif event_class == WATCHER_NOTIFY:
            self.perform_collect_changes()
        elif event_class == WATCHER_SHUTDOWN:
            self.shutdown_auditor_thread()
            audit_thread = self.create_auditor_thread(start=True)
            self.send_administrative_notice(
                subject='"coils.watcher" notification thread resumed.',
                message='"coils.watcher" notification thread resumed.\n'
                        'Component resumed notification at OGo#{0}\n'.
                        format(self.max_audit_entry, ),
                urgency=1,
                category='service', )

    #
    # Perform Handlers
    #

    def perform_collect_changes(self):
        '''
        Collect changs from the audit log.

        00_created,
        02_rejected,
        27_reactivated,
        download
        25_done,
        10_archived
        99_delete
        10_commented
        05_changed
        30_archived
        '''
        object_id = None
        try:
            query = self._ctx.db_session().query(AuditEntry).\
                filter(and_(AuditEntry.object_id > self.max_audit_entry,
                            AuditEntry.action.in_(['00_created',
                                                   '05_changed',
                                                   '99_delete',
                                                   'delete',
                                                   '99_deleted', ]))).\
                order_by(AuditEntry.object_id)

            deletions = {}

            for event in query.all():

                object_id = event.object_id

                if event.action in ('99_delete', '99_deleted', 'delete', ):
                    '''
                    The purpose of this is to supress duplicate deleted
                    notifications with can happen when both a database trigger
                    and a Logic command post a deletion event to the entity
                    audit log.  Processing multiple deletion events is
                    pointless.
                    '''
                    if event.context_id not in deletions:
                        deletions[event.context_id] = event

                else:
                    entity = \
                        self._ctx.type_manager.get_entity(event.context_id)
                    if not entity:
                        continue

                    kind = entity.__entityName__.lower()

                    project_id = 0
                    if hasattr(entity, 'project_id'):
                        project_id = entity.project_id

                    if kind in WATCHED_TYPES:
                        self.log.debug(
                            'Sending event notification for OGo#{0} '
                            '[{1}] "{2}"'.
                            format(event.context_id,
                                   kind,
                                   event.action, ))
                        self.send(
                            Packet(
                                None,
                                'coils.notify/__audit_{0}'.format(kind, ),
                                {'auditId':   event.object_id,
                                 'kind':      kind,
                                 'projectId': project_id,
                                 'objectId':  event.context_id,
                                 'actorId':   event.actor_id,
                                 'action':    event.action,
                                 'message':   event.message, }, ),
                            fanout=True,
                            exchange=NOTIFY_EXCHANGE, )

                self.max_audit_entry = event.object_id

            if deletions:

                for object_id, event in deletions.items():

                    self.send(
                        Packet(
                            None,
                            'coils.notify/__audit_delete',
                            {'auditId':   event.object_id,
                             'kind':      'unknown',
                             'projectId': 0,
                             'objectId':  event.context_id,
                             'actorId':   event.actor_id,
                             'action':    '99_delete',
                             'message':   event.message, }, ),
                        fanout=True,
                        exchange=NOTIFY_EXCHANGE, )

                    self.clean_up(object_id)

            self.persist_max_audit_entry()

        except Exception as e:
            self.log.exception(e)
            self.send_administrative_notice(
                subject='Exception processing database notification',
                message='An exception occured in processing database '
                        'notification OGo#{0}.\n\n{1}\n'.
                        format(object_id,
                               traceback.format_exc(), ),
                urgency=9,
                category='data', )
            self._ctx.rollback()
        else:
            self._ctx.commit()

    def persist_max_audit_entry(self):
        self._ctx.property_manager.set_server_property(
            WATCHER_NAMESPACE,
            'maxAuditEntry',
            self.max_audit_entry, )

    #
    # Cleaner
    #

    def clean_up(self, object_id):

        self.log.debug(
            'Performing maintenance clean-up for deletion of OGo#{0}'.
            format(object_id, ))

        #Object Links
        counter = 0
        query = self._ctx.db_session().query(ObjectLink).\
            filter(or_(ObjectLink.target_id == object_id,
                       ObjectLink.source_id == object_id, ))
        for link in query.all():
            counter += 1
            self._ctx.db_session().delete(link)
        self.log.debug(
            '{0} derelict object links purged for OGo#{1}.'.
            format(counter,
                   object_id, ))

        #Collection Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(CollectionAssignment).\
            filter(CollectionAssignment.assigned_id == object_id)
        for assignment in query.all():
            self._ctx.db_session().delete(assignment)
            counter += 1
        self.log.debug(
            '{0} derelict collection assignments purged for OGo#{1}.'.
            format(counter,
                   object_id, ))

        #Company Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(CompanyAssignment).\
            filter(or_(CompanyAssignment.parent_id == object_id,
                       CompanyAssignment.child_id == object_id, ))
        for assignment in query.all():
            self._ctx.db_session().delete(assignment)
            counter += 1
        self.log.debug(
            '{0} derelict company assignments purged for OGo#{1}.'.
            format(counter,
                   object_id, ))

        #Project Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(ProjectAssignment).\
            filter(or_(ProjectAssignment.parent_id == object_id,
                       ProjectAssignment.child_id == object_id, ))
        for assignment in query.all():
            self._ctx.db_session().delete(assignment)
            counter += 1
        self.log.debug(
            '{0} derelict project assignments purged for OGo#{1}'.
            format(counter, object_id, ))

        #Date Assignments
        counter = 0
        query = self._ctx.db_session().\
            query(Participant).\
            filter(or_(Participant.participant_id == object_id,
                       Participant.appointment_id == object_id, ))
        for participant in query.all():
            self._ctx.db_session().delete(participant)
            counter += 1
        self.log.debug(
            '{0} derelict event participants purged for OGo#{1}'.
            format(counter,
                   object_id, ))

        self.log.debug(
            'Purged {0} orphaned company info entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(CompanyInfo).
                filter(CompanyInfo.parent_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} orphaned date info entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(DateInfo).
                filter(DateInfo.parent_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} orphaned project info entries for OGo#{1}.'.
            format(
                self._ctx.db_session().query(ProjectInfo).
                filter(ProjectInfo.project_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} orphaned object property entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(ObjectProperty).
                filter(ObjectProperty.parent_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} orphaned telephone entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(Telephone).
                filter(Telephone.parent_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} orphaned address entries for OGo#{1}'.
            format(
                self._ctx.db_session().query(Address).
                filter(Address.parent_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} irrelevant locks on OGo#{1}'.
            format(
                self._ctx.db_session().query(Lock).
                filter(Lock.object_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} orphaned process log entries on OGo#{1}'.
            format(
                self._ctx.db_session().query(ProcessLogEntry).
                filter(ProcessLogEntry.process_id == object_id).
                delete(),
                object_id, ))

        self.log.debug(
            'Purged {0} derelict object info entries on OGo#{1}'.
            format(
                self._ctx.db_session().query(ObjectInfo).
                filter(ObjectInfo.object_id == object_id).
                delete(),
                object_id, ))

        return

    #
    # Message Handlers
    #

    def do_set_maxauditentry(self, parameter, packet):
        object_id = long(packet.data.get('maxAuditEntry', 0))
        if object_id:
            self.log.info('Request to reset "maxAuditEntryValue" to {0}'.
                          format(object_id, ))
            self.max_audit_entry = object_id
            self.persist_max_audit_entry()

    def do_get_maxauditentry(self, parameter, packet):
        self.send(
            Packet.Reply(
                packet,
                {'status': 200,
                 'text': 'coils.watcher maxAuditEntry',
                 'value': self.max_audit_entry, }))

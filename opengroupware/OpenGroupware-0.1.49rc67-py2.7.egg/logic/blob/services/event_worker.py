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
import uuid
import traceback
import multiprocessing
import json
from coils.core import \
    send_email_using_project7000_template, \
    MultiProcessWorker, \
    AdministrativeContext

from events import \
    DOCUMENT_COLLECT_REQUEST,\
    DOCUMENT_COLLECT_DISCARDED,\
    DOCUMENT_COLLECT_FAILED,\
    DOCUMENT_COLLECT_COMPLETED,\
    DOCUMENT_DELETED, \
    DOCUMENT_BURST_REQUEST,\
    DOCUMENT_BURST_COMPLETED,\
    DOCUMENT_BURST_FAILED,\
    DOCUMENT_BURST_DISCARDED, \
    DOCUMENT_AUTOFILE_REQUEST, \
    DOCUMENT_AUTOFILE_COMPLETED, \
    DOCUMENT_AUTOFILE_FAILED, \
    DOCUMENT_AUTOFILE_DISCARDED, \
    DOCUMENT_SPECIAL_PROCESSING

from utility import \
    NAMESPACE_MANAGEMENT,\
    ATTR_MANAGEMENT_COLLECTED,\
    ATTR_MANAGEMENT_COLLECTION_DESC,\
    get_inherited_property,\
    expand_labels_in_name,\
    ATTR_MANAGEMENT_BURST_TARGET,\
    ATTR_MANAGEMENT_BURSTED_FLAG, \
    ATTR_MANAGEMENT_AUTOFILE_TARGET

from burst_pdf import DocumentBurst
from autofile_doc import DocumentAutoFile

COMMAND_MAP = {DOCUMENT_COLLECT_REQUEST: 'auto_collect_document',
               DOCUMENT_DELETED: 'process_document_deletion',
               DOCUMENT_AUTOFILE_REQUEST: 'autofile_document',
               DOCUMENT_BURST_REQUEST: 'burst_document',
               DOCUMENT_SPECIAL_PROCESSING: 'special_processing', }

BURSTFAIL_DOCUMENT_TEMPLATE =\
    '/Templates/BurstingFailure.mako'


class EventWorker(MultiProcessWorker):

    def __init__(self, name, work_queue, event_queue, ):
        MultiProcessWorker.__init__(self, name, work_queue, event_queue, )
        self.context = AdministrativeContext()

    def process_worker_message(self, command, payload, ):

        object_id = long(payload.get('objectId', 0))

        self.log.debug(
            'recieved command {0} for OGo#{1}'.
            format(command, object_id, )
        )
        if command in COMMAND_MAP:
            method = 'do_{0}'.format(COMMAND_MAP[command], )
            if hasattr(self, method):
                method = getattr(self, method)
                if method:
                    method(
                        object_id=object_id,
                        action=payload.get('action', 'unknown'),
                        message=payload.get('message', ''),
                        actor_id=payload.get('actorId',  0),
                        project_id=payload.get('projectId',  0),
                    )
            else:
                self.log.error(
                    'Command received with no corresponding implementation; '
                    'looking for "{0}"'.format(method))
        else:
            self.log.error('Unmapped command "{0}" received.'.format(command))
        self.context.db_close()

    def do_auto_collect_document(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
    ):

        document = self.context.run_command('document::get', id=object_id)
        if not document:
            self.enqueue_event(
                DOCUMENT_COLLECT_DISCARDED,
                (object_id, 'Document', 'Document not available', ), )
            return

        prop = self.context.property_manager.get_property(
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_COLLECTED)
        if prop:
            self.enqueue_event(DOCUMENT_COLLECT_DISCARDED,
                               (object_id,
                                'Document',
                                'Document already collected', ), )
            return

        collection_desc = get_inherited_property(
            self.context,
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_COLLECTION_DESC)
        if not collection_desc:
            self.enqueue_event(
                DOCUMENT_COLLECT_DISCARDED,
                (object_id, 'Document', 'No collection path defined.', ), )
            return

        try:
            collection_description = json.loads(collection_desc)
        except:
            self.enqueue_event(
                DOCUMENT_COLLECT_FAILED,
                (object_id, 'Document', traceback.format_exc(), ),
            )
            return
        else:
            collection_name = \
                expand_labels_in_name(collection_description.get('name', None))
            if not collection_name:
                self.enqueue_event(
                    DOCUMENT_COLLECT_FAILED,
                    (object_id,
                     'Document',
                     'Collection description has no name.', ), )
                return

            collection_description['name'] = collection_name

        criteria = [{'key': 'name',
                     'value': collection_description['name'], }, ]
        if collection_description.get('kind', None):
            criteria.append({'key': 'kind',
                             'value': collection_description['kind'], }, )

        collection = self.context.run_command('collection::search',
                                              criteria=criteria)
        if not collection:
            collection = self.context.r_c('collection::new',
                                          values=collection_description)
            collection.project_id = document.project_id
            self.log.info('Automatically created new collection OGo#{0}'.
                          format(collection.object_id))
        else:
            '''
            Searches always have multiple results, we are taking the first one
            '''
            collection = collection[0]
            self.log.debug(
                'Discovered OGo#{0} [Collection] that matches descriptor'.
                format(collection.object_id))

        self.context.r_c('object::assign-to-collection',
                         collection=collection,
                         entity=document)

        self.log.debug(
            'OGo#{0} [Document] automatically joined to OGo#{1} [Collection]'.
            format(document.object_id, collection.object_id, ))

        self.context.pm.set_property(
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_COLLECTED,
            'OGo#{0};name:"{1}";kind:"{2}"'.format(
                collection.object_id,
                collection_description['name'],
                collection_description.get('kind', None)))

        self.log.debug(
            'OGo#{0} [Document] collection join recorded via property'.
            format(document.object_id, ))

        self.context.commit()

        self.log.debug(
            'OGo#{0} [Document] collection join committed.'.
            format(document.object_id, ))

        self.enqueue_event(
            DOCUMENT_COLLECT_COMPLETED,
            (object_id, 'Document', None, ))

        return

    def process_document_deletion(self, object_id):

        # Collections

        # Object-Links

        return

    def do_autofile_document(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
    ):

        # Document Available?
        document = self.context.type_manager.get_entity(object_id)
        if not document:
            self.log.warn(
                'OGo#{0} [Document] not available for auto-file.'.
                format(object_id, ))
            self.enqueue_event(
                DOCUMENT_BURST_FAILED,
                (object_id,
                 'OGo#{0} [Document] not available for auto-file'.
                 format(object_id, ), )
            )
            # Document NOT available
            self.context.rollback()
            return

        # Auto-file Target?
        target_path = get_inherited_property(
            self.context,
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_AUTOFILE_TARGET, )
        if not target_path:
            self.context.rollback()
            self.enqueue_event(
                DOCUMENT_BURST_DISCARDED,
                (object_id, 'No auto-filing target specified.', ), )
            # No burst path
            return

        autofiler = DocumentAutoFile(self.context, document, )

        try:
            target_folder, \
                delete_after, = autofiler.resolve_path(target_path)
        except Exception as exc:
            self.send_administrative_notice(
                subject='Exception auto-filing OGo#{0}'.
                        format(document.object_id, ),
                message='Failure walking auto-file URI to destination.\n'
                        'URI {0}\n'
                        '{1}\n'.format(target_path,
                                       traceback.format_exc(), ),
                urgency=7,
                category='document', )
            self.context.rollback()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_FAILED,
                (object_id,
                 'Attempt to auto-file document OGo#{0} failed'.
                 format(object_id, )), )
            return

        if not target_folder:
            self.log.debug(
                'Target URI "{0}" for auto-filing of OGo#{1} [Document]'
                'cannot be marshalled'.
                format(target_path, document.object_id))
            self.context.rollback()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_FAILED,
                (object_id,
                 'Target  "{0}" does not exist'.format(target_path, )), )
            # Cannot marshall target

            return

        result_code = autofiler.file_to(target_folder)

        if result_code == DOCUMENT_AUTOFILE_COMPLETED:

            if not delete_after:
                self.context.audit_at_commit(
                    object_id=document.object_id,
                    action='10_commented',
                    message='Copy of document auto-filed to OGo#{0}'.
                            format(target_folder.object_id, ))
            else:
                self.context.run_command('document::delete', object=document, )
            self.context.commit()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_COMPLETED,
                (object_id,
                 'Document OGo#{0} auto-filed successfully'.
                 format(object_id, )), )
            return

        elif result_code == DOCUMENT_AUTOFILE_DISCARDED:
            self.context.rollback()
            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Request to auto-file document discarded as a no-op')
            self.context.commit()
            self.enqueue_event(
                DOCUMENT_AUTOFILE_DISCARDED,
                (object_id,
                 'Request to auto-file document OGo#{0} was discarded'.
                 format(object_id, )), )
            return

        # result was neither completed or discarded, so it failed.

        self.context.rollback()
        self.context.audit_at_commit(
            object_id=document.object_id,
            action='10_commented',
            message='Unable to auto-file OGo#{0} to specified target'.
                    format(document.object_id, ))
        self.context.commit()
        self.enqueue_event(
            DOCUMENT_AUTOFILE_FAILED,
            (object_id,
             'Attempt to auto-file document OGo#{0} failed'.
             format(document.object_id, )), )

        return

    def do_burst_document(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
    ):
        '''
          Step 1: is the document available?
          Step 2: is a burst target defined that applies to the document?
          Step 3: has the document already been bursted [avoid loops!]
          Step 4: Burst
          Step 4.1:  create burster
          Step 4.2:  resolve target
          Step 4.3:  burst
          Step 4.4:  burst result notification
        '''

        # Document Available?
        document = self.context.type_manager.get_entity(object_id)
        if not document:
            self.log.warn(
                'OGo#{0} [Document] not available for bursting.'.
                format(object_id, ))
            self.enqueue_event(
                DOCUMENT_BURST_FAILED,
                (object_id,
                 'OGo#{0} [Document] not available for bursting'.
                 format(object_id, ), )
            )
            # Document NOT available
            return

        # Burst Target?
        target_path = get_inherited_property(
            self.context,
            document,
            NAMESPACE_MANAGEMENT,
            ATTR_MANAGEMENT_BURST_TARGET, )
        if not target_path:
            self.enqueue_event(
                DOCUMENT_BURST_DISCARDED,
                (object_id, 'No bursting target specified.', ), )
            # No burst path
            return

        prop = self.context.pm.get_property(document,
                                            NAMESPACE_MANAGEMENT,
                                            ATTR_MANAGEMENT_BURSTED_FLAG)
        if prop:
            self.log.debug(
                'OGo#{0} [Document] has already been bursted @ {1}'.
                format(object_id, prop.get_value(), ))
            self.enqueue_event(
                DOCUMENT_BURST_DISCARDED,
                (object_id,
                 'OGo#{0} has already been bursted or is a burstling'.
                 format(object_id, ), ), )
            # Document has already been bursted
            return

        burster = DocumentBurst(self.context, document, )

        target_folder, \
            copy_enabled, \
            copy_on_failure, \
            error_folder_id, \
            notify_address, = burster.resolve_path(target_path)

        if not target_folder:
            self.log.debug(
                'Target URI "{0}" for bursting of OGo#{1} [Document]'
                'cannot be marshalled'.
                format(target_path, document.object_id))
            self.enqueue_event(
                DOCUMENT_BURST_FAILED,
                (object_id,
                 'Target folder {0} does not exist'.format(target_folder, )), )
            # Cannot marshall target
            return

        self.log.debug(
            'OGo#{0} [Document] will be bursted to OGo#{1}; '
            'copyAllEnabled={2} copyOnFailure={3} errorFolderId={4} '
            'notificationAddress="{5}"'.
            format(document.object_id,
                   target_folder.object_id,
                   copy_enabled,
                   copy_on_failure,
                   error_folder_id,
                   notify_address, ))

        result = burster.burst_to(
            target_folder,
            all_copy_enabled=copy_enabled, )

        if result == DOCUMENT_BURST_FAILED:

            self.context.rollback()

            self.log.debug('bursting failed, rolled back')

            self.context.pm.set_property(document,
                                         NAMESPACE_MANAGEMENT,
                                         ATTR_MANAGEMENT_BURSTED_FLAG,
                                         'FAIL', )

            self.context.pm.set_property(document,
                                         NAMESPACE_MANAGEMENT,
                                         'damaged',
                                         'YES', )

            self.send_initial_bursting_failed_notice(
                document=document,
                target=target_folder,
                exception=burster.last_exception, )

            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Attempt to burst document failed.')

            self.context.commit()

            if notify_address:
                self.send_bursting_failure_notification(
                    document=document,
                    folder=target_folder,
                    exception=burster.last_exception,
                    copy_on_failure=copy_on_failure,
                    to_address=notify_address,
                    copy_enabled=copy_enabled,
                    error_folder_id=error_folder_id,)

            if copy_on_failure:
                if error_folder_id:
                    target_folder = \
                        self.context.run_command('folder::get',
                                                 id=error_folder_id, )
                if not target_folder:
                    self.send_fallback_burst_no_error_folder_notice(
                        document=document,
                        target=target_folder, )
                else:
                    result = burster.copy_to(target_folder)
                    if result == DOCUMENT_BURST_COMPLETED:
                        self.context.audit_at_commit(
                            object_id=document.object_id,
                            action='10_commented',
                            message='Initial bursting failed, fallback copy '
                                    'saved to OGo#{0}'.
                                    format(target_folder.object_id, ))
                        self.context.commit()
                    else:
                        self.send_fallback_burst_failed_notice(
                            document=document,
                            target=target_folder,
                            exception=burster.last_exception,)
                        self.context.rollback()

                        self.context.audit_at_commit(
                            object_id=document.object_id,
                            action='10_commented',
                            message='Attempt to save fallback copy from '
                                    'bursting of document failed.')
                        self.context.commit()

            self.enqueue_event(
                DOCUMENT_BURST_FAILED,
                (object_id,
                 'Bursting of OGo#{0} [Document] failed'.
                 format(document.object_id, ), ), )

        elif result == DOCUMENT_BURST_COMPLETED:
            self.context.pm.set_property(document,
                                         NAMESPACE_MANAGEMENT,
                                         ATTR_MANAGEMENT_BURSTED_FLAG,
                                         'OK')
            self.context.commit()
            self.log.debug('commited bursting')
            self.enqueue_event(DOCUMENT_BURST_COMPLETED, (object_id, ), )
        elif result == DOCUMENT_BURST_DISCARDED:
            self.context.rollback()
            self.log.debug('bursting operation was discarded, rolled back.')
            self.enqueue_event(DOCUMENT_BURST_DISCARDED, (object_id, ), )

        return

    def do_special_processing(
        self,
        object_id,
        action,
        message,
        actor_id,
        project_id,
    ):
        pass

    def send_fallback_burst_failed_notice(
        self,
        document,
        target,
        exception,
    ):
        self.send_administrative_notice(
            subject='Copy-To fallback from document burst failed.',
            message='Copy-To fallback save from bursting of Go#{0} [Document] '
                    '"{1}" failed to OGo#{2} [Folder] "{3}" failed.'
                    '\n-\n{4}\n'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name,
                           exception, ),
            urgency=7,
            category='document', )

    def send_fallback_burst_no_error_folder_notice(
        self,
        document,
        target,
    ):
        self.log.error(
            'Unable to marshall folder for collecting burst failure')
        self.send_administrative_notice(
            subject='Bursting of document failed.'.
                    format(document.object_id, ),
            message='Bursting of OGo#{0} [Document] "{1}" to OGo#{2} '
                    '[Folder] "{2}" failed.'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name, ),
            urgency=7,
            category='document', )

    def send_initial_bursting_failed_notice(
        self,
        document,
        target,
        exception,
    ):
        self.log.error(
            'Unable to marshall folder for collecting burst failure')
        self.send_administrative_notice(
            subject='Bursting of document failed.'.
                    format(document.object_id, ),
            message='Bursting of OGo#{0} [Document] "{1}" to OGo#{2} [Folder] '
                    '"{3}" failed.\n-\n{4}'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name,
                           exception, ),
            urgency=7,
            category='document', )

    def send_autofile_fail_notice(
        self,
        document,
        target,
    ):
        self.log.error(
            'Unable to marshall folder for collecting burst failure')
        self.send_administrative_notice(
            subject='Bursting of document failed.'.
                    format(document.object_id, ),
            message='Bursting of OGo#{0} [Document] "{1}" to OGo#{2} '
                    '[Folder] "{2}" failed.'.
                    format(document.object_id,
                           document.get_file_name(),
                           target.object_id,
                           target.name, ),
            urgency=7,
            category='document', )

    def send_bursting_failure_notification(
        self,
        document,
        folder,
        exception,
        copy_on_failure,
        to_address,
        copy_enabled,
        error_folder_id
    ):
        try:
            mimetype = self.context.type_manager.get_mimetype(document)
            subject = ('Failed to burst OGo#{0} Created In '
                       'burst enabled Folder OGo#{1}'.
                       format(document.object_id,
                              document.folder.object_id, ))
            send_email_using_project7000_template(
                context=self.context,
                subject=subject,
                to_address=to_address,
                template_path=BURSTFAIL_DOCUMENT_TEMPLATE,
                regarding_id=document.object_id,
                parameters={'document': document,
                            'folder': folder,
                            'mimetype': mimetype,
                            'copy_on_failure': copy_on_failure,
                            'traceback': exception,
                            'copy_on_failure': copy_on_failure,
                            'to_address': to_address,
                            'copy_enabled': copy_enabled,
                            'error_folder': error_folder_id, })
        except Exception as exc:
            self.log.error(
                'An exception occurred generating unburstable '
                'notice.')
            self.log.exception(exc)
            self.send_administrative_notice(
                subject='Burster Unable To Generate '
                        'Unburstable Alert For OGo#{0}'.
                        format(document.object_id, ),
                message=traceback.format_exc(),
                urgency=5,
                category='data', )
            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Failed to sent bursting failure notice to "{0}"'.
                        format(to_address, ))
        else:
            self.context.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Bursting failure notice sent to "{0}"'.
                        format(to_address, ))

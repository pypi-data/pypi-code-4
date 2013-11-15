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
import uuid
import cups
import traceback
from coils.core import \
    send_email_using_project7000_template, \
    BLOBManager, \
    AdministrativeContext, \
    ThreadedService, \
    ServerDefaultsManager

global IPP_PRINTABLE_TYPES
global IPP_SERVER_NAME

UNPRINTABLE_DOCUMENT_TEMPLATE =\
    '/Templates/UnprintableDocumentInAutoPrintFolder.mako'

PRINTFAIL_DOCUMENT_TEMPLATE =\
    '/Templates/PrintFailInAutoPrintFolder.mako'


class AutoPrintService(ThreadedService):
    __service__ = 'coils.blob.autoprint'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def setup(self, silent=True):
        '''
        Perform service setup and start all the registered threads.
        '''
        global IPP_PRINTABLE_TYPES
        global IPP_SERVER_NAME

        ThreadedService.setup(self, silent=silent)

        sd = ServerDefaultsManager()
        IPP_PRINTABLE_TYPES = sd.default_as_list('IPPPrintableMIMETypes')
        IPP_SERVER_NAME = \
            sd.string_for_default('DefaultIPPServer', '127.0.0.1')

        self._broker.subscribe('{0}.events'.format(self.__service__, ),
                               self.receive_message,
                               expiration=900000,
                               queue_type='fanout',
                               durable=False,
                               exchange_name='OpenGroupware_Coils_Notify', )

    def prepare(self):
        ThreadedService.prepare(self)

        self._ctx = AdministrativeContext({}, broker=self._broker, )

    def get_autoprint_target_if_defined(self, folder):
        return self._get_inherited_property(
            folder,
            'http://www.opengroupware.us/autoprint',
            'autoPrintQueue')

    def _get_inherited_property(self, folder, namespace, attribute):
        '''
        discover inherited property, rising to the top of the folder
        heirarchy, thus property can be inherited
        '''
        prop = self._ctx.property_manager.get_property(
            folder,
            namespace,
            attribute)
        if not prop:
            tmp = folder.folder
            while tmp:
                prop = self._ctx.property_manager.get_property(
                    tmp,
                    namespace,
                    attribute)
                if prop:
                    break
                tmp = tmp.folder
        if not prop:
            self.log.debug(
                'No inherited property {{{0}}}{1} on OGo#{2} [Folder]'.
                format(namespace, attribute, folder.object_id))
            return None
        return prop.get_string_value()

    def _print_document(self, print_queue, mimetype, folder, document):
        global IPP_SERVER_NAME

        rfile = self._ctx.run_command('document::get-handle',
                                      document=document, )
        if not rfile:
            return

        try:
            cups.setServer(IPP_SERVER_NAME)
            ipp_connection = cups.Connection()
            ipp_connection.printFile(
                print_queue,
                rfile.name,
                document.get_file_name(),
                {'media': 'Letter',
                 'fit-to-page': str('yes'), })
            BLOBManager.Close(rfile)
            ipp_connection = None
        except Exception as exc:
            msg = traceback.format_exc()
            self.log.exception(exc)
            self._send_printfail_notice(folder=folder,
                                        document=document,
                                        mimetype=mimetype,
                                        print_queue=print_queue,
                                        _traceback=msg, )
            self._ctx.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Document created in auto-print folder '
                        'failed to be queued to {0}@{1}'.
                        format(print_queue, IPP_SERVER_NAME))
        else:
            self._ctx.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Document created in auto-print folder '
                        'successfully queued to {0}@{1}'.
                        format(print_queue, IPP_SERVER_NAME))

    def _send_printfail_notice(self,
                               folder,
                               document,
                               mimetype,
                               print_queue,
                               _traceback):
        to_address = self._get_inherited_property(
            folder,
            'http://www.opengroupware.us/autoprint',
            'printFailAlertAddress')
        if not to_address:
            return
        self.log.debug(
            'Notification of print attempt failure will attempt to'
            ' be delivered to "{0}"'.format(to_address, ))

        '''
        Generate and send the message
        '''
        try:
            subject = ('Failed to queue OGo#{0} Created In '
                       'Auto-Print Enabled Foder OGo#{1}'.
                       format(document.object_id,
                              folder.object_id, ))
            send_email_using_project7000_template(
                self._ctx, subject=subject,
                to_address=to_address,
                template_path=PRINTFAIL_DOCUMENT_TEMPLATE,
                regarding_id=document.object_id,
                parameters={'document': document,
                            'folder': folder,
                            'mimetype': mimetype,
                            'printqueue': print_queue,
                            'traceback': _traceback, })
        except Exception as exc:
            self.log.error(
                'An exception occurred generating unprintable '
                'notice.')
            self.log.exception(exc)
            self.send_administrative_notice(
                subject='Auto-Print Service Unable To Generate '
                        'Unprintable Alert For OGo#{0}'.
                        format(document.object_id, ),
                message=traceback.format_exc(),
                urgency=5,
                category='data', )
            self._ctx.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Failed to sent auto-print failure notice to "{0}"'.
                        format(to_address, ))
        else:
            self._ctx.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Auto-print failure notice sent to "{0}"'.
                        format(to_address, ))

    def _send_unprintable_notice(self,
                                 folder,
                                 document,
                                 mimetype,
                                 damaged,
                                 print_queue):

        to_address = self._get_inherited_property(
            folder,
            'http://www.opengroupware.us/autoprint',
            'unprintableAlertAddress')
        if not to_address:
            return
        self.log.debug(
            'Notification of unprintable document will attempt to'
            ' be delivered to "{0}"'.format(to_address, ))

        '''
        Generate and send the message
        '''
        try:
            subject = ('Unprintable Document OGo#{0} Created In '
                       'Auto-Print Enabled Foder OGo#{1}'.
                       format(document.object_id,
                              folder.object_id, ))
            send_email_using_project7000_template(
                self._ctx,
                subject=subject,
                to_address=to_address,
                template_path=UNPRINTABLE_DOCUMENT_TEMPLATE,
                regarding_id=document.object_id,
                parameters={'document': document,
                            'folder': folder,
                            'mimetype': mimetype,
                            'damaged': damaged,
                            'printqueue': print_queue, })
        except Exception as exc:
            self.log.error(
                'An exception occurred generating unprintable '
                'notice.')
            self.log.exception(exc)
            self.send_administrative_notice(
                subject='Auto-Print Service Unable To Generate '
                        'Unprintable Alert For OGo#{0}'.
                        format(document.object_id, ),
                message=traceback.format_exc(),
                urgency=5,
                category='data', )

    #
    # Message Handlers
    #

    def do___audit_document(self, parameter, packet):

        global IPP_PRINTABLE_TYPES

        object_id = long(packet.data.get('objectId', 0))
        action_tag = packet.data.get('action', 'unknown')
        print_queue = None

        if not action_tag == '00_created':
            return

        self.log.debug(
            'Autoprint service attempting to queue OGo#{0} [Document]'.
            format(object_id, ))

        document = self._ctx.run_command('document::get', id=object_id)
        if not document:
            self.log.error(
                'Unable to marshall OGo#{0} [Document]'.
                format(object_id, ))
            return

        if not document.folder_id:
            self.log.error(
                'OGo#{0} [Document] is not assigned a folder'.
                format(object_id, ))
            return

        folder = self._ctx.run_command('folder::get',
                                       id=document.folder_id, )
        if not folder:
            self.log.debug('Cannot marshall OGo#{0} [Folder]'.
                           format(folder.object_id, ))
            return

        print_queue = self.get_autoprint_target_if_defined(folder)

        if not print_queue:
            self.log.debug(
                'No autoprint target for OGo#{0} [Document] in '
                'OGo#{1} [Folder] '.
                format(document.object_id, folder.object_id, ))
            return

        self.log.debug(
            'Autoprint for OGo#{0} [Document] in OGo#{1} [Folder] '
            'targeted to "{2}"'.
            format(document.object_id,
                   folder.object_id,
                   print_queue, )
        )

        mimetype = self._ctx.type_manager.get_mimetype(document)

        prop = self._ctx.property_manager.get_property(
            document,
            '57c7fc84-3cea-417d-af54-b659eb87a046',
            'damaged'
        )
        if prop:
            damaged = prop.get_string_value()
        else:
            damaged = 'NO'

        if (mimetype in IPP_PRINTABLE_TYPES) and (damaged != 'YES'):
            self._print_document(print_queue=print_queue,
                                 folder=folder,
                                 mimetype=mimetype,
                                 document=document)
        else:

            if damaged == 'YES':
                self.log.info(
                    'Suspectedly damaged document created in autoprint'
                    ' folder.')
            else:
                self.log.info(
                    'Document created in autoprint folder of an '
                    'unprintable type "{0}"'.format(mimetype, ))

            self._send_unprintable_notice(folder=folder,
                                          document=document,
                                          mimetype=mimetype,
                                          damaged=damaged,
                                          print_queue=print_queue, )

            self._ctx.audit_at_commit(
                object_id=document.object_id,
                action='10_commented',
                message='Document created in auto-print folder '
                        'determined to be unprintable')

        self._ctx.commit()
        self._ctx.db_close()

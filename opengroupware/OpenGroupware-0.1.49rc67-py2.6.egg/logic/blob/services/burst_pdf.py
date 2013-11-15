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
import logging

import shutil

import signal

import time

import random

import traceback

from coils.foundation.api.pypdf2 import PdfFileReader, PdfFileWriter

from coils.core import \
    walk_ogo_uri_to_folder, \
    Document, \
    Folder, \
    CoilsException, \
    parse_ogo_uri, \
    BLOBManager

from utility import \
    NAMESPACE_MANAGEMENT, \
    ATTR_MANAGEMENT_SOURCE_DOCUMENT_ID, \
    ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE, \
    ATTR_MANAGEMENT_BURSTED_FLAG, \
    ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE_COUNT

from events import \
    DOCUMENT_BURST_COMPLETED,\
    DOCUMENT_BURST_FAILED,\
    DOCUMENT_BURST_DISCARDED

CONVERSION_TIMEOUT_SECONDS = 60


class TimeOutAlarm(Exception):
    pass


def timeout_alarm_handler(signum, frame):
    raise TimeOutAlarm


class BurstingTimeOutException(Exception):
    pass


class DocumentBurst(object):

    def __init__(self, ctx, document, ):
        self.context = ctx
        self.document = document
        self.last_page_count = 0
        self.log = logging.getLogger(
            'coils.blob.burster.{0}'.format(document.object_id))

    @staticmethod
    def GenerateUniqueFileName(document, counter=0):
        if document.extension:
            return '{0}-{1:0>5}-{2}-{3}.{4}'.\
                   format(document.name.lower(),
                          counter,
                          long(time.time() * 1000),
                          random.randrange(10000, 99999),
                          document.extension, )
        else:
            return '{0}-{1:0>5}-{2}-{3}'.\
                   format(document.name.lower(),
                          counter,
                          long(time.time() * 1000),
                          random.randrange(10000, 99999), )

    def resolve_path(self, target_path):

        all_copy_enabled = False
        copy_on_failure = False
        error_folder_id = None
        on_fail_notify = None
        folder, arguments, = \
            walk_ogo_uri_to_folder(context=self.context,
                                   uri=target_path,
                                   create_path=True,
                                   default_params={'allcopyenabled': 'NO',
                                                   'copyonfailure': 'NO',
                                                   'errorfolderid': None,
                                                   'onfailnotify': None, })
        if arguments['allcopyenabled'].upper() == 'YES':
            all_copy_enabled = True
        if arguments['copyonfailure'].upper() == 'YES':
            copy_on_failure = True
        if arguments['errorfolderid']:
            error_folder_id = long(arguments['errorfolderid'])
        on_fail_notify = arguments['onfailnotify']

        return \
            folder, \
            all_copy_enabled, \
            copy_on_failure, \
            error_folder_id, \
            on_fail_notify

    def burst_to(
        self,
        folder,
        all_copy_enabled=False,
    ):
        self.last_page_count = 0
        self.last_exception = None
        mimetype = self.context.type_manager.get_mimetype(self.document)
        if mimetype in ('application/pdf', 'application/x-pdf', ):
            self.log.info(
                'PDF document OGo#{0} will be page bursted'.
                format(self.document.object_id))
            return self.burst_pdf_to(folder=folder)
        elif all_copy_enabled:
            self.log.info(
                'Non-PDF document, bursting OGo#{0} as whole document copy'.
                format(self.document.object_id))
            return self.copy_to(folder=folder)
        else:
            return DOCUMENT_BURST_DISCARDED

    def copy_to(self, folder):

        filename = DocumentBurst.GenerateUniqueFileName(self.document)

        if self.document.folder.object_id == folder.object_id:
            burstling = self.document
        else:
            rfile = self.context.run_command('document::get-handle',
                                             document=self.document, )
            if not rfile:
                return DOCUMENT_BURST_FAILED
            burstling = self.context.run_command(
                'document::new',
                folder=folder,
                name=filename,
                handle=rfile,
                values={}, )

        self.post_processing(burstling=burstling,
                             counter=0,
                             of_pages=0, )

        self.log.info(
            'Bursted copy of OGo#{0} is OGo#{1} in OGo#{2}'.
            format(self.document.object_id,
                   burstling.object_id,
                   burstling.folder.object_id))

        return DOCUMENT_BURST_COMPLETED

    def burst_pdf_to(self, folder):

        rfile = self.context.run_command('document::get-handle',
                                         document=self.document, )
        if not rfile:
            self.context.log.error(
                'Handle for OGo#{0} [Document] cannot be marshalled'.
                format(self.document.object_id))
            return DOCUMENT_BURST_FAILED

        signal.signal(signal.SIGALRM, timeout_alarm_handler)
        try:
            pages = []

            reader = PdfFileReader(rfile, strict=False, )
            of_pages = reader.getNumPages()
            for page in range(0, reader.getNumPages()):
                #
                try:
                    signal.alarm(CONVERSION_TIMEOUT_SECONDS)
                    sfile = BLOBManager.ScratchFile()
                    writer = PdfFileWriter()
                    writer.addPage(reader.getPage(page))
                    writer.write(sfile)
                    writer = None
                    signal.alarm(0)
                    sfile.seek(0)
                    pages.append(sfile)
                except TimeOutAlarm:
                    raise BurstingTimeOutException
                finally:
                    signal.alarm(0)

            reader = None

            counter = 1
            for rfile in pages:
                filename = \
                    DocumentBurst.GenerateUniqueFileName(self.document,
                                                         counter=counter)
                burstling = self.context.r_c('document::new',
                                             folder=folder,
                                             name=filename,
                                             handle=rfile,
                                             values={}, )
                self.post_processing(burstling=burstling,
                                     counter=counter,
                                     of_pages=of_pages, )
                self.log.info(
                    'Page {0} burstling of OGo#{1} is OGo#{2} in OGo#{3}'.
                    format(counter,
                           self.document.object_id,
                           burstling.object_id,
                           burstling.folder.object_id))
                # Close the origin file
                BLOBManager.Close(rfile)
                # Indicate the page counter
                self.last_page_count = counter
                counter += 1

            pages = None

        except Exception as exc:
            if isinstance(exc, BurstingTimeOutException):
                self.log.error(
                    'A time-out occured during PDF burst of OGo#{0}'.
                    format(self.document.object_id, ))
            else:
                self.log.error(
                    'Unexpected exception occurred in PDF bursting'
                    ' of OGo#{0} [Document]'.
                    format(self.document.object_id, ))
            self.log.exception(exc)
            self.last_exception = \
                '{0}\n{1}'.format(exc,
                                  traceback.format_exc())
            return DOCUMENT_BURST_FAILED
        else:
            self.context.audit_at_commit(
                object_id=self.document.object_id,
                action='10_commented',
                message='Document bursted to {0} pages into OGo#{1}'.
                        format(self.last_page_count, folder.object_id, ))
            return DOCUMENT_BURST_COMPLETED
        finally:
            pass

    def post_processing(self, burstling, counter, of_pages):

        burstling.owner_id = self.document.owner_id

        # Copy properties from the origin document to the burstling
        for prop in self.context.pm.get_properties(self.document):
            self.context.property_manager.set_property(
                entity=burstling,
                namespace=prop.namespace,
                attribute=prop.name,
                value=prop.get_value(), )

        self.context.pm.set_property(
            entity=burstling,
            namespace=NAMESPACE_MANAGEMENT,
            attribute=ATTR_MANAGEMENT_SOURCE_DOCUMENT_ID,
            value=self.document.object_id, )

        if counter:
            self.context.pm.set_property(
                entity=burstling,
                namespace=NAMESPACE_MANAGEMENT,
                attribute=ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE,
                value=counter, )

        if of_pages:
            self.context.pm.set_property(
                entity=burstling,
                namespace=NAMESPACE_MANAGEMENT,
                attribute=ATTR_MANAGEMENT_SOURCE_DOCUMENT_PAGE_COUNT,
                value=of_pages, )

        self.context.pm.set_property(
            entity=burstling,
            namespace=NAMESPACE_MANAGEMENT,
            attribute=ATTR_MANAGEMENT_BURSTED_FLAG,
            value='TARGET', )

        # Create link indicating source document
        self.context.link_manager.link(
            burstling,
            self.document,
            kind='coils:burstedFrom',
            label='Document Burst')

        self.context.link_manager.copy_links(self.document, burstling)

        if counter:
            self.context.audit_at_commit(
                object_id=burstling.object_id,
                action='10_commented',
                message='Created by page bursting of document OGo#{0} from '
                        'folder OGo#{1}. This document represents page {2} '
                        'of the source document'.
                        format(self.document.object_id,
                               self.document.folder.object_id,
                               counter, ))
        else:
            self.context.audit_at_commit(
                object_id=burstling.object_id,
                action='10_commented',
                message='Created by page bursting of document OGo#{0} from '
                        'folder OGo#{1}'.
                        format(self.document.object_id,
                               self.document.folder.object_id, ))

        return

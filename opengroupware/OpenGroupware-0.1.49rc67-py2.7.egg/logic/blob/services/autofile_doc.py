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

import time

import random

from coils.core import \
    walk_ogo_uri_to_folder, \
    CoilsException

from utility import \
    expand_labels_in_name

from events import \
    DOCUMENT_AUTOFILE_COMPLETED, \
    DOCUMENT_AUTOFILE_FAILED, \
    DOCUMENT_AUTOFILE_DISCARDED

CONVERSION_TIMEOUT_SECONDS = 60


class DocumentAutoFile(object):

    def __init__(self, ctx, document, ):
        self.context = ctx
        self.document = document
        self.log = logging.getLogger(
            'coils.blob.autofile.{0}'.format(document.object_id))

    @staticmethod
    def GenerateUniqueFileName(document):
        if document.extension:
            return '{0}-{1}-{2}.{3}'.\
                   format(document.name.lower(),
                          long(time.time() * 1000),
                          random.randrange(10000, 99999),
                          document.extension, )
        else:
            return '{0}-{1}-{2}'.\
                   format(document.name.lower(),
                          long(time.time() * 1000),
                          random.randrange(10000, 99999), )

    def resolve_path(self, target_path):

        target_path = expand_labels_in_name(target_path)
        self.log.debug('expanded path for auto-filing is "{0}"'.
                       format(target_path, ))
        delete_after = False
        folder, arguements, = None, None,
        try:
            folder, arguments, = \
                walk_ogo_uri_to_folder(context=self.context,
                                       uri=target_path,
                                       create_path=True,
                                       default_params={
                                           'deleteafterfiling': 'NO',
                                       })
        except Exception as exc:
            self.log.error('Exception walking path from OGo URI "{0}"'.
                           format(target_path, ))
            self.log.exception(exc)
            return None
        if arguments['deleteafterfiling'].upper() == 'YES':
            delete_after = True

        return \
            folder, \
            delete_after

    def file_to(self, folder):

        filename = DocumentAutoFile.GenerateUniqueFileName(self.document)

        if self.document.folder.object_id == folder.object_id:
            return DOCUMENT_AUTOFILE_DISCARDED
        else:
            if self.document.file_size < 1:
                return DOCUMENT_AUTOFILE_DISCARDED

            rfile = self.context.run_command('document::get-handle',
                                             document=self.document, )
            if not rfile:
                return DOCUMENT_AUTOFILE_FAILED

            filed_copy = self.context.run_command(
                'document::new',
                folder=folder,
                name=filename,
                handle=rfile,
                values={}, )

        self.post_processing(filed_copy=filed_copy, )

        self.log.info(
            'Filed copy of OGo#{0} is OGo#{1} in OGo#{2}'.
            format(self.document.object_id,
                   filed_copy.object_id,
                   filed_copy.folder.object_id))

        return DOCUMENT_AUTOFILE_COMPLETED

    def post_processing(self, filed_copy):

        filed_copy.owner_id = self.document.owner_id

        # Copy properties from the origin document to the burstling
        for prop in self.context.pm.get_properties(self.document):
            self.context.property_manager.set_property(
                entity=filed_copy,
                namespace=prop.namespace,
                attribute=prop.name,
                value=prop.get_value(), )

        self.context.link_manager.copy_links(self.document, filed_copy)

        # Create link indicating source document
        self.context.link_manager.link(
            filed_copy,
            self.document,
            kind='coils:copyFrom',
            label='Filed Copy')

        return

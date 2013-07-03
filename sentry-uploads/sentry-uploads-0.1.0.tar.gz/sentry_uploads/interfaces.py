"""
sentry_uploads.interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Process Systems Enterprise.
:license: BSD, see LICENSE for more details.
"""

import os.path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import Http404

from sentry.conf import settings
from sentry.interfaces import Interface
from sentry.plugins import plugins
from sentry.utils.strings import decompress
from sentry.web.helpers import render_to_string

from sentry_uploads.plugin import UploadsPlugin

class Uploads(Interface):
    """
    Uploaded files of arbitrary size.
    """

    attrs = ('files',)

    def __init__(self, files):
        self.files = files

    def get_path(self, filename):
        return os.path.join('uploads', filename)

    def save(self, file):
        filename = self.get_path(file['filename'])
        contents = decompress(file['data'])
        del file['data']
        file['path'] = default_storage.save(filename, ContentFile(contents))
        contents = None

        file['size'] = default_storage.size(file['path'])
        if not 'type' in file:
            file['type'] = None

        return file

    def validate(self):

        # This should only be called when the event is received,
        # prior to the file being stored
        assert len(self.files) > 0
        assert not any(['path' in file for file in self.files])
        assert all(['data' in file for file in self.files])

        self.files = [self.save(file) for file in self.files]

    def get_filenames(self):
        return [file['filename'] for file in self.files]

    def get_hash(self):
        return self.get_filenames()

    def get_search_context(self, event):
        return {
            'text': self.get_filenames()
        }

    def to_string(self, event, is_public = False, **kwargs):
        return render_to_string('sentry_uploads/uploads.txt', {
            'files': [{
                'filename': file['filename'],
                'deleted': file.get('deleted', False),
                'size': file['size'],
            } for file in self.files],
        })

    def to_html(self, event, is_public = False, **kwargs):
        try:
            plugin = plugins.get(UploadsPlugin.slug)
        except KeyError:
            raise Http404('Plugin not found')

        return render_to_string('sentry_uploads/uploads.html', {
            'files': [{
                'filename': file['filename'],
                'deleted': file.get('deleted', False),
                'type': file['type'],
                'size': file['size'],
                'urls': {
                    'download': plugin.get_action_url(event.group, 'download', file['filename']),
                    'delete': plugin.get_action_url(event.group, 'delete', file['filename']),
                },
            } for file in self.files],
        })

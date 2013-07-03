"""
sentry_uploads.plugin
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Process Systems Enterprise
:license: BSD, see LICENSE for more details.
"""

import mimetypes
import urllib
import urlparse

from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from sentry.models import Event
from sentry.plugins import Plugin

import sentry_uploads

class UploadsPlugin(Plugin):
    author = 'Duane Griffin'
    author_url = 'https://github.com/duaneg/sentry-uploads'
    version = sentry_uploads.VERSION
    description = "Allow clients to attach files to events."
    resource_links = [
        ('Bug Tracker', 'https://github.com/duaneg/sentry-uploads/issues'),
        ('Source', 'https://github.com/duaneg/sentry-uploads'),
    ]

    slug = 'uploads'
    title = _('Uploads')
    conf_title = title
    conf_key = 'uploads'

    def get_action_url(self, group, action, filename = None):
        base = urlparse.urlparse(self.get_url(group))
        query = urlparse.parse_qs(base.query)
        query['action'] = action
        if filename:
            query['filename'] = filename
        parts = list(base)
        parts[4] = urllib.urlencode(query)
        return urlparse.urlunparse(parts)

    def actions(self, request, group, action_list, **kwargs):
        action_list.append((_('Delete all files'), self.get_action_url(group, 'delete_all')))
        return action_list

    def get_view_response(self, request, group):
        self.selected = request.path == self.get_url(group)
        if not self.selected:
            return

        if request.REQUEST['action'] == 'download':
            return self.serve_file(request, group)
        elif request.REQUEST['action'] == 'delete':
            return self.delete_file(request, group)
        elif request.REQUEST['action'] == 'delete_all':
            return self.delete_all(request, group)

    def get_file(self, group, filename):
        event = group.get_latest_event() or Event()
        for iface in event.interfaces.itervalues():
            if not isinstance(iface, sentry_uploads.interfaces.Uploads):
                continue

            for file in iface.files:
                if file['filename'] == filename:
                    return (event, file)

    def serve_file(self, request, group):
        file = self.get_file(group, request.REQUEST['filename'])[1]
        if not file or file.get('deleted', False):
            return

        fh = default_storage.open(file['path'])
        if not fh:
            return

        type = file['type']
        if type is None:
            type = mimetypes.guess_type(file['filename'])

        response = HttpResponse(ChunkedFile(fh), content_type = type)
        response['Content-Disposition'] = smart_str(u'attachment; filename=%s' % file['filename'])
        if not file['size'] is None:
            response['Content-Length'] = file['size']

        return response

    def delete_all(self, request, group):
        for event in group.event_set.all():
            for iface in event.interfaces.itervalues():
                if not isinstance(iface, sentry_uploads.interfaces.Uploads):
                    continue

                for file in iface.files:
                    self.do_delete_file(event, file)

        # TODO: Need to redirect here, but don't have the team...

    def delete_file(self, request, group):
        (event, file) = self.get_file(group, request.REQUEST['filename'])
        self.do_delete_file(event, file)

        # TODO: Need to redirect here, but don't have the team...

    def do_delete_file(self, event, file):
        if not file or file.get('deleted', False):
            return

        default_storage.delete(file['path'])
        file['deleted'] = True
        event.save()

class ChunkedFile(object):
    def __init__(self, file):
        self.file = file

    def __iter__(self):
        return self.file.chunks()

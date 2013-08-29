#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import AdministrativeContext
from coils.core import NoSuchPathException
from coils.core import BLOBManager
from coils.core import ObjectInfo
from coils.core import CoilsException
from coils.core import NotImplementedException
from coils.core import Document
from coils.core import Folder
from coils.core import get_yaml_struct_from_project7000
from coils.net import PathObject, Protocol

from site_page import SitePage
from site_folder import SiteFolder

from dispatcher import Dispatcher


class Sites(Protocol, PathObject):
    '''
    Root  of the /site protocol.
    '''
    __pattern__ = ['^site$', '^s$', ]
    __namespace__ = None
    __xmlrpc__ = False

    def __init__(self, parent, parameters, request):
        super(Sites, self).__init__(parent=parent,
                                    parameters=parameters,
                                    request=request)

    @property
    def ctx(self):
        return self.context

    def get_name(self):
        return 'sites'

    def is_public(self):
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        dispatcher = self.get_dispatcher()
        if not dispatcher:
            raise NoSuchPathException(
                'No site-project exists for Host: == {0}'.
                format(host_requested))

        # Create content index
        contents = self.ctx.r_c('folder::ls',
                                folder=dispatcher.project.folder, )
        index = {}
        for content in contents:
            if isinstance(content, Folder):
                index[content.name] = content
            elif isinstance(content, Document):
                if content.extension:
                    if content.extension in ('mako', ):
                        continue
                    index[content.get_display_name()] = content

        target = index.get(name, None)
        if not target:
            target = index.get('{0}.markdown'.format(name), None)

        if isinstance(target, Document):
            return SitePage(parent=self,
                            ctx=self.ctx,
                            document=target,
                            request=self.request,
                            dispatcher=self.dispatcher,
                            name=name)
        elif isinstance(target, Folder):
            return SiteFolder(parent=self,
                              ctx=self.ctx,
                              folder=target,
                              request=self.request,
                              dispatcher=dispatcher,
                              parameters=self.parameters)

        raise NoSuchPathException(
            'No such target as "{0}" in site project {1}'.
            format(name, dispatcher.project))

    def do_HEAD(self):
        self.request.simple_response(204)

    def do_GET(self):
        dispatcher = self.get_dispatcher()

        contents = self.ctx.r_c('folder::ls',
                                folder=dispatcher.project.folder,
                                name='index.markdown')

        if contents:
            page = SitePage(parent=self,
                            ctx=self.ctx,
                            dispatcher=dispatcher,
                            document=contents[0],
                            request=self.request)
            page.do_GET()
            return

        raise NoSuchPathException(
            'No such target as "{0}" in site project {1}'.
            format('index', dispatcher.project))

    def get_dispatcher(self):

        host_requested = self.request.headers.get('Host', None)

        if not host_requested:
            # TODO: this should probably be a bad-request response
            raise UnimplementedException('Request with no Host: header')

        # Deal with the fact that the Host: header can include the port#
        host_requested = host_requested.lower().split(':')[0]

        site_map = get_yaml_struct_from_project7000(
            context=self.ctx,
            path='/Sites/SiteMap.yaml',
            access_check=False)

        project_number = site_map.get(host_requested, None)
        if not project_number:
            self.log.error(
                'Network context cannot marshall project with'
                ' number "{0}"'.format(project_number))
            return None

        project = self.ctx.r_c('project::get', number=project_number)
        if not project:
            raise NoSuchPathcException(
                'Site project cannot be marshalled')

        self.log.debug('Found OGo#{0} for site "{1}"'.
                       format(project.object_id, host_requested))
        return Dispatcher(context=self.ctx, project=project)

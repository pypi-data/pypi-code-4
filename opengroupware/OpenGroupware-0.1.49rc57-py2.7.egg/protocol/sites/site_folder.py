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
from coils.core import NoSuchPathException
from coils.core import Document
from coils.core import Folder

from site_object import SiteObject
from site_page import SitePage


class SiteFolder(SiteObject):
    '''
    Responds to a request whose URI equals the path to a project
    folder.  Either the request is descending to a document or
    sub-folder or the index.markdown document is proxied to a
    SitePage object.
    '''

    def __init__(self, ctx, parent, parameters, request, folder, dispatcher):
        self.folder = folder
        super(SiteFolder, self).__init__(parent=parent,
                                         ctx=ctx,
                                         parameters=parameters,
                                         request=request)
        self.dispatcher = dispatcher

    def get_name(self):
        return self.folder.name

    def is_public(self):
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        # Create content index
        contents = self.ctx.r_c('folder::ls',
                                folder=self.folder, )
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
                            dispatcher=self.dispatcher,
                            request=self.request,
                            name=name)
        elif isinstance(target, Folder):
            return SiteFolder(parent=self,
                              ctx=self.ctx,
                              folder=target,
                              request=self.request)

        raise NoSuchPathException(
            'No such target as "{0}" in folder {1}'.
            format(name, self.dispatcher.project))

    def do_HEAD(self):
        self.request.simple_response(204)

    def do_GET(self):
        contents = self.ctx.r_c('folder::ls',
                                folder=self.folder,
                                name='index.markdown')

        if contents:
            page = SitePage(parent=self,
                            ctx=self.ctx,
                            dispatcher=self.dispatcher,
                            document=contents[0],
                            request=self.request)
            page.do_GET()
            return

        raise NoSuchPathException(
            'No such target as "{0}" in site project {1}'.
            format('index', self.dispatcher.project))

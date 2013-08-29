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
import shutil
from mako.template import Template

from coils.foundation import BLOBManager
from coils.core import NoSuchPathException

from site_object import SiteObject
from markdown_content import MarkdownContent


class SitePage(SiteObject):
    '''
    Represents a document via the /sites protocol.  A page
    corresponds to a Markdown document that will be wrapped in a
    Mako template.
    '''

    def __init__(self, parent, **params):
        SiteObject.__init__(self, parent, **params)

    def get_name(self):
        return self.document.name

    @property
    def mimetype(self):
        return self.content_type

    def render(self, stream):

        self.content_type = self.ctx.tm.get_mimetype(self.document)

        title = self.document.name
        if not title:
            title = 'Untitled'

        if not self.content_type == 'text/x-markdown':
            shutil.copyfileobj(self.ctx.r_c('document::get-handle',
                                            document=self.document),
                               stream)
            return

        # Find a template
        template = None
        template_id = self.ctx.pm.get_property(self.document,
                                               'sites',
                                               'templateObjectId')
        if template_id:
            template_id = long(template_id.get_value())
            template = self.ctx.r_c('document::get', id=template_id)
        else:
            template = self.ctx.r_c('folder::ls',
                                    folder=self.document.folder,
                                    name='template.mako')
            if template:
                template = template[0]

        if not template:
            raise NoSuchPathException(
                'No Mako template available to encapsulate content')

        #Render
        template_rfile = self.ctx.r_c('document::get-handle',
                                      document=template)

        content = MarkdownContent(context=self.ctx,
                                  document=self.document)

        template_data = template_rfile.read()
        stream.write(Template(template_data).
                     render(**{'ogo': self.dispatcher,
                               'doc': content, }))
        self.content_type = 'text/html'

        return

    def do_GET(self):
        sfile = BLOBManager.ScratchFile()
        self.render(sfile)
        sfile.seek(0)
        self.request.stream_response(200,
                                     stream=sfile,
                                     mimetype=self.content_type)
        return

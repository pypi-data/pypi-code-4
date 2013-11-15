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
import markdown  # pylint: disable-msg=F0401
from site_content import SiteContent
from extensions import OGoBLOGRollExt, OGoIndexTableExt


class MarkdownContent(SiteContent):   # pylint: disable-msg=R0903
    '''
    SiteContent object which renders Markdown to HTML5
    '''

    def __init__(self, context, document):
        SiteContent.__init__(self, context=context)
        self.document = document

    @property
    def name(self):
        return self.document.name

    def render(self):
        rfile = self.ctx.r_c('document::get-handle',
                             document=self.document)
        mde = markdown.Markdown(
            extensions=['toc', 'tables', 'footnotes',
                        OGoBLOGRollExt({'context': self.ctx,
                                        'folder': self.document.folder,
                                        }),
                        OGoIndexTableExt({'context': self.ctx,
                                          'folder': self.document.folder,
                                          'document': self.document,
                                          }), ],
            output_format='html5')

        html = mde.convert(rfile.read())

        return html

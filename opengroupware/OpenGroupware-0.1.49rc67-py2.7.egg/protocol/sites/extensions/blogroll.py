#
# Copyright (c) 2013 Tauno Williams <awilliam@whitemice.org>
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
import datetime
from argparse import ArgumentParser
from coils.core import Folder, Document, utf8_split
import markdown
from markdown.util import etree


def get_parser():
    '''
    Parse the content of the OGOBLOGRoll Markdown block
    '''
    parser = ArgumentParser(prefix_chars=':')

    subs = parser.add_subparsers(dest="subparser")

    column_parser = subs.add_parser('display', prefix_chars=':')
    column_parser.add_argument('::count',  action='store', type=int)

    query_parser = subs.add_parser('query', prefix_chars=':')
    query_parser.add_argument('::folder',  action='store', type=str)

    return parser


class OGoBLOGRollProcessor(markdown.blockprocessors.BlockProcessor):
    '''
    Process OGo Blog Roll Folder, render the Markdown documents
    found into HTML DIVs.
    '''

    def test(self, parent, block):
        '''
        Return true if the provided blob is an OGoBLOGRoll
        '''
        rows = [row.strip() for row in block.split('\n')]
        result = (len(rows) > 2 and
                  rows[0].startswith('{OGoBLOGRoll{') and
                  rows[-1].endswith('}OGoBLOGRoll}'))
        return result

    def run(self, parent, blocks):
        '''
        Use the blocks parameters to build a series of divs
        representing the most recent articles.
        '''

        article_count = 5
        blog_folder = 'blog'

        parser = get_parser()

        """ Parse a table block and build table. """
        block = blocks.pop(0).split('\n')
        datum = block[1:-1]
        for line in datum:
            line = utf8_split(line)
            args = parser.parse_args(line)
            if args.subparser == 'display':
                article_count = args.count
            elif args.subparser == 'query':
                blog_folder = args.folder

        # Retrieve target folder
        folder = self.ctx.r_c('folder::ls',
                              name=blog_folder,
                              folder=self.folder)
        if not folder:
            ''' If no corresponding folder exists the module silently
                exit; then the module doesn't render anything. '''
            return

        folder = folder[0]

        if not isinstance(folder, Folder):
            ''' If the search for the folder returns something other
                than a folder (such as a document or link) then the
                module doesn't render anything. It exists silently. '''
            return

        # Retrieve, order, and potentially reduce the document list
        documents = self.ctx.r_c('folder::ls', folder=folder)
        documents = [d for d in documents
                     if isinstance(d, Document) and
                     d.extension == 'markdown']
        documents = sorted(documents,
                           key=lambda document: document.created,
                           reverse=True)
        documents = documents[:article_count]

        # Render BLOG Article divs

        html_stash = self.parser.markdown.htmlStash

        for document in documents:

            divp = etree.SubElement(parent, 'div')

            divt = etree.SubElement(divp, 'div')
            a = etree.SubElement(divt, 'a')
            # TODO: This should use the actual path to this obejct
            a.set('href',
                  'site/{0}/{1}'.format(blog_folder, document.name))
            a.text = html_stash.store('<h1>{0}</h1>'.
                                      format(document.name))

            divb = etree.SubElement(divp, 'div')
            rfile = self.ctx.r_c('document::get-handle',
                                 document=document)
            if not rfile:
                ''' Skip an artcle if the handle cannot be opened.'''
                continue

            mde = markdown.Markdown(
                extensions=['tables', 'footnotes', ],
                output_format='html5')

            html = mde.convert(rfile.read())

            divb.text = html_stash.store(html, safe=True)


class OGoBLOGRollExt(markdown.Extension):
    '''
    Encapsulate the OGoBLOGRoll block processor into a markdown
    extension.  The extension requires a folder and a context.
    '''

    def __init__(self, configs):
        self.ctx = configs.get('context', None)
        self.folder = configs.get('folder', None)

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of TableProcessor to BlockParser. """
        ext = OGoBLOGRollProcessor(md.parser)
        ext.ctx = self.ctx
        ext.folder = self.folder
        md.parser.blockprocessors.add('ogoblogroll', ext, '<hashheader')


def makeExtension(configs={}):
    return OGoBLOGRollExt(configs=configs)

#
# Copyright (c) 2012, 2013 Tauno Williams <awilliam@whitemice.org>
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
import markdown
import datetime
from argparse import ArgumentParser
from markdown.util import etree
from coils.core import Folder, Document, utf8_split


def get_parser():
    parser = ArgumentParser(prefix_chars=':')

    subs = parser.add_subparsers(dest="subparser")

    column_parser = subs.add_parser('include', prefix_chars=':')
    column_parser.add_argument('::folders', action='store_true',
                               default=False)
    column_parser.add_argument('::documents',  action='store_true',
                               default=False)
    column_parser.add_argument('::mimetypes', action='store',
                               default='any')

    display_parser = subs.add_parser('display', prefix_chars=':')
    display_parser.add_argument('::border',     action='store_true',
                                dest="border", default=False)

    column_parser = subs.add_parser('column', prefix_chars=':')
    column_parser.add_argument('::title', action='store', type=str,)
    column_parser.add_argument('::alignment',  action='store', default='left', choices=['right', 'left', 'center', ],)
    column_parser.add_argument('::link',  action='store_true', default=False,)
    column_parser.add_argument('::attribute',  action='store', type=str,)
    column_parser.add_argument('::format',  action='store', type=str, default='%Y-%m-%d')

    return parser


class OGoIndexTableProcessor(markdown.blockprocessors.BlockProcessor):
    """ Present an index of available folders and documents """

    def test(self, parent, block):
        rows = [row.strip() for row in block.split('\n')]
        result = (len(rows) > 2 and
                  rows[0].startswith('{OGoIndexTable{') and
                  rows[-1].endswith('}OGoIndexTable}'))
        return result

    def run(self, parent, blocks):

        include_mimetypes = 'application/octet-stream'
        parser = get_parser()

        """ Parse a table block and build table. """
        block = blocks.pop(0).split('\n')
        datum = block[1:-1]
        # parse datum
        border = False
        include_documents = False
        include_folders = False
        columns = []
        for line in datum:
            line = utf8_split(line)
            args = parser.parse_args(line)
            if args.subparser == 'display':
                border = args.border
            elif args.subparser == 'column':
                columns.append(args)
            elif args.subparser == 'include':
                include_documents = args.documents
                include_folders = args.folders
                include_mimetypes = args.mimetypes
        include_mimetypes = [unicode(x) for x in include_mimetypes.split(',')]
        # Build table
        table = etree.SubElement(parent, 'table')
        if border:
            table.set('border', '1')
        thead = etree.SubElement(table, 'thead')

        print 'COLUMNS', columns

        # execute query
        search_result = []
        contents = self.ctx.run_command('folder::ls', folder=self.folder)
        for entity in contents:
            if entity.object_id == self.document.object_id:
                # do not include ourselves
                continue
            elif isinstance(entity, Document) and include_documents:
                if ((self.ctx.tm.get_mimetype(entity) in include_mimetypes) or
                   (include_mimetypes[0] == 'any')):
                    search_result.append(entity)

        # build header
        self._header_row(thead, columns, border)
        tbody = etree.SubElement(table, 'tbody')
        # build rows
        for record in search_result:
            self._result_row(record, tbody, columns, border)

    def _header_row(self, parent, columns, border):
        tr = etree.SubElement(parent, 'tr')
        tag = 'th'
        for column in columns:
            c = etree.SubElement(tr, tag)
            c.text = column.title

    def _result_row(self, entity, parent, columns, border):
        """ Given a row of text, build table cells. """
        tr = etree.SubElement(parent, 'tr')
        tag = 'td'
        for column in columns:
            c = etree.SubElement(tr, tag)
            try:
                value = getattr(entity, column.attribute)
                if value is None:
                    value = ''
                    c.set('class', 'value-null')
                elif isinstance(value, list):
                    value = ','.join(value)
                elif isinstance(value, datetime.datetime):
                    try:
                        value = value.strftime(column.format)
                    except Exception as e:
                        c.text = "!DATE FORMAT ERROR!"
                        c.set('class', 'value-error')
                elif isinstance(value, basestring):
                    pass
                else:
                    value = unicode(value)
                if column.link:
                    a = etree.SubElement(c, 'a')
                    a.text = value
                    a.set('href', 'OGo#{0}'.format(entity.object_id))
                else:
                    c.text = value
            except Exception as e:
                c.text = "!ERROR!"
                c.set('class', 'value-error')
            c.set('align', column.alignment)

    def _header_row(self, parent, columns, border):
        tr = etree.SubElement(parent, 'tr')
        tag = 'th'
        for column in columns:
            c = etree.SubElement(tr, tag)
            c.text = column.title

    def _result_row(self, entity, parent, columns, border):
        """ Given a row of text, build table cells. """
        tr = etree.SubElement(parent, 'tr')
        tag = 'td'
        for column in columns:
            c = etree.SubElement(tr, tag)
            try:
                value = getattr(entity, column.attribute)
                if value is None:
                    value = ''
                elif isinstance(value, list):
                    value = ','.join(value)
                elif isinstance(value, datetime.datetime):
                    try:
                        value = value.strftime(column.format)
                    except Exception as e:
                        c.text = "!DATE FORMAT ERROR!"
                        c.set('class', 'value-error')
                elif isinstance(value, basestring):
                    pass
                else:
                    value = unicode(value)
                if column.link:
                    a = etree.SubElement(c, 'a')
                    a.text = value
                    a.set('href', entity.get_display_name())
                else:
                    c.text = value
            except Exception as e:
                c.text = "!ERROR!"
                print e
            c.set('align', column.alignment)


class OGoIndexTableExt(markdown.Extension):

    def __init__(self, configs):
        self.ctx = configs.get('context', None)
        self.folder = configs.get('folder', None)
        self.document = configs.get('document', None)

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of TableProcessor to BlockParser. """
        ext = OGoIndexTableProcessor(md.parser)
        ext.ctx = self.ctx
        ext.folder = self.folder
        ext.document = self.document
        md.parser.blockprocessors.add('ogoindextable', ext, '<hashheader')


def makeExtension(configs={}):
    return OGoIndexTableExt(configs=configs)

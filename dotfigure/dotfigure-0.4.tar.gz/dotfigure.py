# -*- encoding: utf-8 -*-

"""

Graphviz graph figure directive

"""

from os.path import dirname, abspath, join, normpath, splitext, basename
from subprocess import check_call, CalledProcessError
from itertools import count
from tempfile import NamedTemporaryFile
from re import compile, UNICODE
from xml.etree import ElementTree as ETree
from xml.etree.ElementTree import ParseError
from docutils.nodes import raw, reference
from docutils.utils import relative_path
from docutils.utils.error_reporting import ErrorString
from docutils.parsers.rst.directives.images import Image
from docutils.parsers.rst.directives.body import CodeBlock
from docutils.parsers.rst.directives import register_directive
from docutils.parsers.rst.directives import choice, unchanged, flag, path, uri, class_option
from docutils.parsers.rst import Directive

_output_types = {
    'bmp': 'image/bmp',
    'gif': 'image/gif',
    'ico': 'image/x-ico',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'jpe': 'image/jpeg',
    'png': 'image/png',
    'webp': 'image/webp',
    'svg': 'image/svg+xml',
    'svgz': 'image/svg+xml',
    'vml': 'application/vnd.openxmlformats-officedocument.vmlDrawing',
    'vmlz': 'application/vnd.openxmlformats-officedocument.vmlDrawing',
    'eps': 'image/x-eps',
    'ps': 'application/postscript',
    'ps:cairo': 'application/postscript',
    'fig': 'application/x-xfig',
    'pdf': 'application/pdf',
    'tif': 'image/tiff',
    'tiff': 'image/tiff',
    'wbmp': 'image/vnd.wap.wbmp',
    'canon': 'text/plain',
    'dot': 'text/plain',
    'xdot': 'text/plain',
    'gv': 'text/plain',
    'plain': 'text/plain',
    'plain-ext': 'text/plain',
    'pov': 'text/x-povray',
    'pic': 'image/x-pict',
    'tk': 'text/x-tcl'
}

class DotFigure(Directive):
    """
    Graphviz graph figure directive.

    Graph source can be included inline or provided as an external file
    with file or url options.

    Directive contains code from:
    docutils/parsers/rst/directives/misc.py (Include and Raw directives)
    docutils/parsers/rst/directives/image.py (Image directive)
    """

    def layout(argument):
        return choice(argument, ('dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp'))

    counter = count().next

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'format': unchanged,
        'layout': layout,
        'datauri': flag,
        'inline': flag,
        'nofigure': flag,
        'file': path,
        'url': uri,
        # codeblock opts
        'number-lines': unchanged, # integer or None
        # image opts
        'alt': unchanged,
        'height': unchanged,
        'width': unchanged,
        'scale': unchanged,
        'align': unchanged,
        'target': unchanged,
        # common opts
        'class': class_option,
        'name': unchanged,
    }
    has_content = True

    def run(self):
        if (not self.state.document.settings.file_insertion_enabled
            and ('file' in self.options
                 or 'url' in self.options)):
            raise self.warning('"%s" directive disabled.' % self.name)

        output_format = self.options.pop('format', 'png')
        output_layout = self.options.pop('layout', 'dot')
        output_inline = not self.options.pop('inline', True)
        output_datauri = not self.options.pop('datauri', True)
        output_nofigure = not self.options.pop('nofigure', True)
        if 'name' in self.options:
            output_filename = '%s.%s' % (basename(self.options['name']),
                output_format)
        else:
            output_filename = 'dotfigure-%i.%s' % (self.counter(), output_format)
        source_dir = dirname(abspath(self.state.document.current_source))
        output_path = normpath(join(source_dir, output_filename))
        output_path = relative_path(None, output_path)
        command = ['dot']
        command_args = {}
        command.extend(('-T', output_format))
        command.extend(('-K', output_layout))
        command.extend(('-o', output_path))

        if output_format not in _output_types:
            raise self.error(
                'The output format (%s) is not allowed for '
                '"%s" directive.' %
                (output_format, self.name))

        if self.content:
            if 'file' in self.options or 'url' in self.options:
                raise self.error(
                    '"%s" directive may not both specify an external file '
                    'and have content.' % self.name)
            dot_file = NamedTemporaryFile()
            dot_file.writelines(s.encode('utf-8') for s in self.content)
            dot_file.seek(0)
            command_args['stdin'] = dot_file
        elif 'file' in self.options:
            if 'url' in self.options:
                raise self.error(
                    'The "file" and "url" options may not be simultaneously '
                    'specified for the "%s" directive.' % self.name)
            path = self.options.pop('file')
            path = normpath(join(source_dir, path))
            path = relative_path(None, path)
            command.append(path)
        elif 'url' in self.options:
            source = self.options.pop('url')
            # Do not import urllib2 at the top of the module because
            # it may fail due to broken SSL dependencies, and it takes
            # about 0.15 seconds to load.
            import urllib2
            try:
                result = urllib2.urlopen(source)
            except (urllib2.URLError, IOError), error:
                raise self.severe(u'Problems with "%s" directive URL "%s":\n%s.'
                    % (self.name, source, ErrorString(error)))
            command_args['stdin'] = result.fp

        try:
            check_call(command, **command_args)
        except (CalledProcessError, OSError), error:
            self.error(u'Problem with "%s" directive os command: %s' %
                (self.name, ErrorString(error)))

        self.state.document.settings.record_dependencies.add(output_path)

        if output_nofigure:
            return []

        if output_format in ('canon', 'dot', 'xdot', 'plain',
                'plain-ext','gv', 'tk', 'pov'):
            codeblock = CodeBlock(self.name,
                                  [], # arguments
                                  self.options,
                                  open(output_path, 'rb').readlines(), # content
                                  self.lineno,
                                  self.content_offset,
                                  self.block_text,
                                  self.state,
                                  self.state_machine)
            return codeblock.run()

        if output_inline:
            if output_datauri:
                raise self.error(
                    'The "inline" and "datauri" options may not be simultaneously '
                    'specified for the "%s" directive.' % self.name)
            if output_format not in ('svg', 'vml'):
                raise self.error(
                    'The "inline" option and the %s "format" option may not '
                    'be simultaneously specified for the "%s" directive.' %
                        (output_format, self.name))
            try:
                xmlstring = \
                    ETree.tostring(ETree.parse(output_path, 'utf-8').getroot())
            except (IOError, ParseError), error:
                raise self.error(
                    'Problem in "%s" directive xml parser: %s' %
                        (self.name, ErrorString(error)))
            attributes = {'format': 'html xml',
                          'source': output_path}
            raw_node = raw('', xmlstring, **attributes)
            (raw_node.source, raw_node.line) = \
                self.state_machine.get_source_and_line(self.lineno)
            return [raw_node]

        if output_datauri:
            data = open(output_path, 'rb').read()
            data = data.encode('base64').replace('\n', '')
            output_uri = 'data:%s;base64,%s' % (_output_types[output_format], data)
        else:
            output_uri = output_filename

        if output_format in ('pdf', 'ps', 'ps:cairo', 'fig'):
            reference_node = reference(refuri=output_uri,
                text=output_filename, title=output_filename)
            return [reference_node]

        if 'alt' not in self.options:
            self.options['alt'] = output_filename

        image = Image(self.name,
                      [output_uri], # arguments
                      self.options,
                      [], # content
                      self.lineno,
                      self.content_offset,
                      self.block_text,
                      self.state,
                      self.state_machine)
        return image.run()

def register():
    register_directive('dotfigure', DotFigure)


# Copyright (C) 2012-2013 Steven Myint

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Formats docstrings to follow PEP 257."""

from __future__ import print_function

import errno
import io
import os
import re
import tokenize


__version__ = '0.2.7'


try:
    unicode
except NameError:
    unicode = str


def format_code(source,
                summary_wrap_length=0,
                pre_summary_newline=False,
                post_description_blank=True):
    """Return source code with docstrings formatted.

    Wrap summary lines if summary_wrap_length is greater than 0.

    """
    sio = io.StringIO(source)
    formatted = ''
    previous_token_string = ''
    previous_token_type = None
    previous_line = ''
    last_row = 0
    last_column = -1
    for token in tokenize.generate_tokens(sio.readline):
        token_type = token[0]
        token_string = token[1]
        start_row, start_column = token[2]
        end_row, end_column = token[3]
        line = token[4]

        # Preserve escaped newlines
        if (not previous_line.lstrip().startswith('#') and
            start_row > last_row and
                (previous_line.endswith('\\\n') or
                 previous_line.endswith('\\\r\n') or
                 previous_line.endswith('\\\r'))):
            formatted += previous_line[len(previous_line.rstrip(' \t\n\r\\')):]

        # Preserve spacing
        if start_row > last_row:
            last_column = 0
        if start_column > last_column:
            formatted += line[last_column:start_column]

        if (token_type == tokenize.STRING and
                starts_with_triple(token_string) and
                previous_token_type == tokenize.INDENT):
            formatted += format_docstring(
                previous_token_string,
                token_string,
                summary_wrap_length=summary_wrap_length,
                pre_summary_newline=pre_summary_newline,
                post_description_blank=post_description_blank)
        else:
            formatted += token_string

        previous_token_string = token_string
        previous_token_type = token_type
        previous_line = line

        last_row = end_row
        last_column = end_column

    return formatted


def starts_with_triple(string):
    """Return True if the string starts with triple single/double quotes."""
    return (string.strip().startswith('"""') or
            string.strip().startswith("'''"))


def format_docstring(indentation, docstring,
                     summary_wrap_length=0,
                     pre_summary_newline=False,
                     post_description_blank=True):
    """Return formatted version of docstring.

    Wrap summary lines if summary_wrap_length is greater than 0.

    Relevant parts of PEP 257:
        - For consistency, always use triple double quotes around docstrings.
        - Triple quotes are used even though the string fits on one line.
        - Multi-line docstrings consist of a summary line just like a one-line
          docstring, followed by a blank line, followed by a more elaborate
          description.
        - The BDFL recommends inserting a blank line between the last paragraph
          in a multi-line docstring and its closing quotes, placing the closing
          quotes on a line by themselves.

    """
    contents = strip_docstring(docstring)

    # Skip if there are nested triple double quotes
    if contents.count('"""'):
        return docstring

    summary, description = split_summary_and_description(contents)

    if description:
        # Compensate for triple quotes by temporarily prepending 3 spaces.
        # This temporary prepending is undone below.
        if pre_summary_newline:
            initial_indent = indentation
        else:
            initial_indent = 3 * ' ' + indentation

        return '''\
"""{pre_summary}{summary}

{description}{post_description}
{indentation}"""\
'''.format(pre_summary=('\n' + indentation if pre_summary_newline
                        else unicode()),
           summary=wrap_summary(normalize_summary(summary),
                                wrap_length=summary_wrap_length,
                                initial_indent=initial_indent,
                                subsequent_indent=indentation).lstrip(),
           description='\n'.join([indent_non_indented(l, indentation).rstrip()
                                  for l in description.splitlines()]),
           post_description=('\n' if post_description_blank else unicode()),
           indentation=indentation)
    else:
        return wrap_summary('"""' + normalize_summary(contents) + '"""',
                            wrap_length=summary_wrap_length,
                            initial_indent=indentation,
                            subsequent_indent=indentation).strip()


def indent_non_indented(line, indentation):
    """Return indented line if it has no indentation."""
    if line.lstrip() == line:
        return indentation + line
    else:
        return line


def split_summary_and_description(contents):
    """Split docstring into summary and description.

    Return tuple (summary, description).

    """
    split = contents.splitlines()
    if len(split) > 1 and not split[1].strip():
        # Empty line separation would indicate the rest is the description.
        return (split[0], '\n'.join(split[2:]))
    elif len(split) > 1 and not split[1].strip()[0].isalnum():
        # Symbol on second line probably is a description with a list.
        return (split[0], '\n'.join(split[1:]))
    else:
        # Break on first sentence.
        split = re.split(r'\.\s', string=contents, maxsplit=1)
        if len(split) == 2:
            return (split[0].strip() + '.', split[1].strip())
        else:
            return (split[0].strip(), unicode())


def strip_docstring(docstring):
    """Return contents of docstring."""
    triple = '"""'
    if docstring.lstrip().startswith("'''"):
        triple = "'''"
        assert docstring.rstrip().endswith("'''")

    return docstring.split(triple, 1)[1].rsplit(triple, 1)[0].strip()


def normalize_summary(summary):
    """Return normalized docstring summary."""
    # Remove newlines
    summary = re.sub(r'\s*\n\s*', ' ', summary.rstrip())

    # Add period at end of sentence
    if summary and summary[-1].isalnum():
        summary += '.'

    return summary


def wrap_summary(summary, initial_indent, subsequent_indent, wrap_length):
    """Return line-wrapped summary text."""
    if wrap_length > 0:
        import textwrap
        return '\n'.join(
            textwrap.wrap(summary,
                          width=wrap_length,
                          initial_indent=initial_indent,
                          subsequent_indent=subsequent_indent)).strip()
    else:
        return summary


def open_with_encoding(filename, encoding, mode='r'):
    """Return opened file with a specific encoding."""
    return io.open(filename, mode=mode, encoding=encoding,
                   newline='')  # Preserve line endings


def detect_encoding(filename):
    """Return file encoding."""
    try:
        with open(filename, 'rb') as input_file:
            from lib2to3.pgen2 import tokenize as lib2to3_tokenize
            encoding = lib2to3_tokenize.detect_encoding(input_file.readline)[0]

            # Check for correctness of encoding.
            with open_with_encoding(filename, encoding) as input_file:
                input_file.read()

        return encoding
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return 'latin-1'


def format_file(filename, args, standard_out):
    """Run format_code() on a file."""
    encoding = detect_encoding(filename)
    with open_with_encoding(filename, encoding=encoding) as input_file:
        source = input_file.read()
        formatted_source = format_code(
            source,
            summary_wrap_length=args.wrap_summaries,
            pre_summary_newline=args.pre_summary_newline,
            post_description_blank=args.post_description_blank)

    if source != formatted_source:
        if args.in_place:
            with open_with_encoding(filename, mode='w',
                                    encoding=encoding) as output_file:
                output_file.write(formatted_source)
        else:
            import difflib
            diff = difflib.unified_diff(
                io.StringIO(source).readlines(),
                io.StringIO(formatted_source).readlines(),
                'before/' + filename,
                'after/' + filename)
            standard_out.write(unicode().join(diff))


def main(argv, standard_out, standard_error):
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, prog='docformatter')
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='make changes to files instead of printing diffs')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='drill down directories recursively')
    parser.add_argument(
        '--wrap-summaries', default=79, type=int, metavar='length',
        help='wrap long summary lines at this length (default: %(default)s)')
    parser.add_argument('--no-blank', dest='post_description_blank',
                        action='store_false',
                        help='do not add blank line after description')
    parser.add_argument('--pre-summary-newline',
                        action='store_true',
                        help='add a newline before the summary of a '
                             'multi-line docstring')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+',
                        help='files to format')

    args = parser.parse_args(argv[1:])

    filenames = list(set(args.files))
    while filenames:
        name = filenames.pop(0)
        if args.recursive and os.path.isdir(name):
            for root, directories, children in os.walk(name):
                filenames += [os.path.join(root, f) for f in children
                              if f.endswith('.py') and
                              not f.startswith('.')]
                for d in directories:
                    if d.startswith('.'):
                        directories.remove(d)
        else:
            try:
                format_file(name, args=args, standard_out=standard_out)
            except IOError as exception:
                if exception.errno == errno.EPIPE:
                    return
                print(exception, file=standard_error)

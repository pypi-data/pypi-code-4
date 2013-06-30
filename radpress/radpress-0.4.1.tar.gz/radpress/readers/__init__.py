import importlib
import os
import sys
from django.utils.encoding import smart_str

from radpress.settings import DEFAULT_MARKUP


class BaseReader(object):
    """
    Thanks to pelican contributors.
    """
    name = None
    enabled = False
    initial = ''

    def __init__(self, source):
        self.source = smart_str(source)


def get_reader(markup=None):
    if markup is None:
        markup = DEFAULT_MARKUP

    module_path = 'radpress.readers.%s_reader' % markup
    reader = importlib.import_module(module_path).Reader
    return reader


def get_reader_initial(markup=None):
    reader = get_reader(markup=markup)
    return trim(reader.initial)


def get_markup_choices():
    """
    Receives available markup options as list.
    """
    available_reader_list = []
    module_dir = os.path.realpath(os.path.dirname(__file__))
    module_names = filter(
        lambda x: x.endswith('_reader.py'), os.listdir(module_dir))

    for module_name in module_names:
        markup = module_name.split('_')[0]
        reader = get_reader(markup=markup)

        if reader.enabled is True:
            available_reader_list.append((markup, reader.name))

    return available_reader_list


def trim(docstring):
    # from: http://stackoverflow.com/questions/2504411/
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

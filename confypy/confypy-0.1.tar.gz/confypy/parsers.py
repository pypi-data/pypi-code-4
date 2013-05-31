import os

try:
    from json import loads as json
except ImportError:
    from simplejson import loads as json

try:
    from yaml import load as yaml
except ImportError as e:
    error = e
    def yaml(value):
        raise error

from .compat import StringIO
from .compat import SafeConfigParser
from .compat import string_type
from .exceptions import ParserNotFound


def configparser(data):
    result = {}

    strio = StringIO()
    strio.write(data)
    strio.seek(0)

    parser = SafeConfigParser()
    parser.readfp(strio)

    for section in parser.sections():
        section_data = {}

        for key, value in parser.items(section):
            section_data[key] = value

        result[section] = section_data

    return result


def parser_from_parser_or_filename(parser, filename):

    if callable(parser):
        return parser

    if isinstance(parser, string_type):
        return parser_for_ext(parser)

    return parser_for_filename(filename)


def parser_for_filename(filename):
    ext = os.path.splitext(filename)[1][1:].strip().lower()

    if ext:
        return parser_for_ext(ext)
    else:
        return lambda x: x


def parser_for_ext(ext):

    mapping = {
    'yml': yaml,
    'yaml': yaml,
    'json': json,
    'ini': configparser,
    'configparser': configparser
    }

    result = mapping.get(ext.lower(), None)

    if result:
        return result

    raise ParserNotFound(ext)

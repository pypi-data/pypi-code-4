#! /usr/bin/env python
"""
Some IO functions for CmtStandardNames package.
"""

import os

from cmt.standard_names import (StandardName, Collection, BadNameError)
from cmt.standard_names import (format_as_wiki, format_as_yaml)
from cmt.standard_names import (google_doc, url, plain_text)


class Error(Exception):
    """Base exception for this module."""
    pass


class BadIntentError(Error):
    """Error to indicate a bad key for intent."""
    def __init__(self, key, valid_keys):
        super(BadIntentError, self).__init__()
        self._key = key
        self._valid_keys = valid_keys

    def __str__(self):
        return '%s: Should be one of %s' % (self._key,
                                            ','.join(self._valid_keys))


def _list_to_string(lines, **kwds):
    """
    Concatonate a list of strings into one big string using the line separator
    as a joiner.

    :lines: List of strings
    :keyword sorted: Sort lines before joining
    :returns: Joined lines as a string
    """
    sort_list = kwds.pop('sorted', False)

    if sort_list:
        sorted_lines = list(lines)
        sorted_lines.sort()
        return os.linesep.join(sorted_lines)
    else:
        return os.linesep.join(lines)


def _scrape_stream(stream, regex=r'\b\w+__\w+'):
    """
    Scrape standard names from stream matching a regular expression.

    :stream: A file-like object.
    :keyword regex: A regular expression as a string
    :returns: Scraped words as a Collection
    """
    import re
    names = Collection()

    text = stream.read()
    words = re.findall(regex, text)
    for word in words:
        try:
            names.add(word)
        except BadNameError:
            print word

    return names


FORMATTERS = dict(plain=_list_to_string)
for (name, decorator) in [('wiki', format_as_wiki), ('yaml', format_as_yaml)]:
    FORMATTERS[name] = decorator(_list_to_string)


SCRAPERS = dict()
for decorator in [google_doc, url, plain_text]:
    SCRAPERS[decorator.__name__] = decorator(_scrape_stream)


_VALID_INTENTS = ['input', 'output']

def _find_unique_names(models):
    """
    Find unique names in a iterable of StandardNames.

    :models: A dictionary of model information
    :returns: A Collection of the unique names
    """
    names = Collection()
    for model in models:
        if isinstance(model['exchange items'], dict):
            new_names = []
            for intent in model['exchange items']:
                try:
                    assert(intent in _VALID_INTENTS)
                except AssertionError:
                    raise BadIntentError(intent, _VALID_INTENTS)
                new_names.extend(model['exchange items'][intent])
        else:
            new_names = model['exchange items']

        for name in new_names:
            names.add(StandardName(name))

    return names


def from_model_file(stream):
    """
    Get standard names from a YAML file listing standard names for particular
    models and produce the corresponding Collection.

    :stream: YAML stream
    :returns: A Collection
    """
    import yaml
    models = yaml.load_all(stream)
    names = _find_unique_names(models)
    return names


def scrape(name, **kwds):
    """
    Scrape standard names for a named source.

    :name: Name of the source as a string
    :keyword format: The format of the source
    :returns: A Collection
    """
    source_format = kwds.pop('format', 'url')

    return SCRAPERS[source_format](name, **kwds)

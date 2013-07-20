"""
Ax_FuzzyTourney - input formats.

Provides means of loading primary data set (tournament competitors).

This module is not intended for public use.
User formats (subclass InputFormat) may be defined separately and used by 
full dotted path to class in tournament config.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import sys
import csv
import fileinput
import StringIO

import axonchisel.fuzzytourney.error as error


# ----------------------------------------------------------------------------


class InputFormat(object):
    """Input format superclass."""
    def __init__(self, config):
        raise NotImplementedError()
    def read_entrants(self):
        """Abstract: Read input and return list of (abstract) entrants."""
        raise NotImplementedError()


# ----------------------------------------------------------------------------


class InputFormatBase(InputFormat):
    """Input format common superclass."""
    def __init__(self, config):
        self._config = config
        self._src = config.get('src', None)
    def override_src(self, src):
        """Allow override of src to new filename."""
        self._src = src
    def _config_req(self, key):
        """Return param from config dict, or raise error if missing."""
        if key not in self._config:
            raise error.ConfigIncompleteError("Missing config param '{0}' in input '{1}'.".
                format(key, self.__class__.__name__))
        return self._config[key]


# ----------------------------------------------------------------------------


class InputFormat_Inline(InputFormatBase):
    """
    Input format for taking input directly from tournament data.
    Config example: { "data": [10, 20, 50, 30, 7, 90] }
    Required param "data" is used as entrant list.
    """
    def __init__(self, config):
        InputFormatBase.__init__(self, config)
        self._data = self._config_req('data')
    def read_entrants(self):
        """Abstract: Read input and return list of (abstract) entrants."""
        return self._data

class InputFormat_Text_Lines(InputFormatBase):
    """
    Input format for handling text stream, one item per line.
    Allow "-" (default) for source to read from STDIN.
    Config example: { "src": "src_filename.txt" }
    """
    def __init__(self, config):
        InputFormatBase.__init__(self, config)
        self._line_num = 0  # of last read line, 1-based.
    def read_entrants(self):
        """Abstract: Read input and return list of (abstract) entrants."""
        entrants = []
        for line in fileinput.input(self._src):
            self._line_num += 1
            line = line.rstrip()
            entrant = self._convert(line)
            entrants.append(entrant)
        return entrants
    def _convert(self, line):
        """
        Allow subclasses to convert line string to entrant data format,
        or None to skip this item.
        """
        return line

class InputFormat_Text_Lines_Int(InputFormat_Text_Lines):
    """
    Input format for handling text stream, one int item per line.
    Allow "-" (default) for source to read from STDIN.
    Config example: { "src": "src_filename.txt" }
    """
    def _convert(self, line):
        """
        Allow subclasses to convert line string to entrant data format,
        or None to skip this item.
        """
        try:
            return int(line)
        except ValueError as e:
            raise error.InputError(u"Invalid int '{0}' on line {1}".format(line, self._line_num))

class InputFormat_Text_CSV(InputFormatBase):
    """
    Input format for handling text stream, one CSV item per line.
    Allow "-" (default) for source to read from STDIN.
    Creates entrants that are lists.
    Config example: { "src": "src_filename.txt" , "dialect": "excel" }
    Config:
     - csv_header = "ids", or "no".
     - src = "filename" or "-" for STDOUT
     - dialect = "excel" or "excel-tab", ...
     - struct = "list" or "dict"
    """
    def __init__(self, config):
        InputFormatBase.__init__(self, config)
        self._dialect = config.get('dialect', 'excel')
        self._csv_header = config.get('csv_header', 'no')
        self._struct = config.get('struct', 'list')
        self._line_num = 0   # of last read line, 1-based.
        self._header = None  # list of field ids if specified
        self._csvin = None
    def read_entrants(self):
        """Abstract: Read input and return list of (abstract) entrants."""
        entrants = []

        want_header = False
        if self._csv_header != 'no':
            if self._csv_header == 'ids':
                want_header = True
            else:
                raise error.ConfigValueError("Invalid csv_header mode '{0}' in input format".format(self._csv_header))
        
        raw_text = "".join(fileinput.input(self._src))
        self._csvin = csv.reader(StringIO.StringIO(raw_text), dialect=self._dialect)
        for rec in self._csvin:
            if want_header:
                self._header = rec
                want_header = False
                continue
            if self._struct == 'list':
                pass
            elif self._struct == 'dict':
                rec = self._list_to_dict(rec)
            else:
                raise error.ConfigValueError("Invalid struct mode '{0}' in input format".format(self._struct))
            entrants.append(rec)
        return entrants
    def _list_to_dict(self, rec):
        """Return dict version (using header ids) of row read (as list)."""
        return dict(zip(self._header, rec))
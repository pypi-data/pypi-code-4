"""
Ax_FuzzyTourney - output formats.

Provides means of outputting tournament results.

This module is not intended for public use.
User formats (subclass OutputFormat) may be defined separately and used by 
full dotted path to class in tournament config.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from __future__ import print_function

import sys
import csv
import json

import axonchisel.fuzzytourney.error as error


# ----------------------------------------------------------------------------


class OutputFormat(object):
    """Output format interface/superclass."""
    def __init__(self, options):
        raise NotImplementedError()
    def open(self, tournament, entrants):
        """Abstract: Open and write header to output."""
        raise NotImplementedError()
    def entrant(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Write results for single entrant to output."""
        raise NotImplementedError()
    def close(self):
        """Abstract: Write footer to output and close."""
        raise NotImplementedError()
    

# ----------------------------------------------------------------------------


class OutputFormatBase(OutputFormat):
    """Output format common superclass."""
    def __init__(self, options):
        self._options = options
        self._dest = options.get('dest', None)
        self._tournament = None
        self._f = None
    def override_dest(self, dest):
        """Allow override of dest to new filename."""
        self._dest = dest
    def open(self, tournament, entrants):
        """Abstract: Open and write header to output."""
        self._tournament = tournament
        self._entrants = entrants
    def _open_file(self, fname):
        """Helper: open named file (or "-" for STDOUT) for writing."""
        if (fname == '-'):
            self._f = sys.stdout
        else:
            self._f = open(fname, 'wb')
    def _close_file(self, fname):
        """Helper: close named file (or "-" for STDOUT, ignored) after writing."""
        if (fname == '-'):
            return
        else:
            self._f.close()


# ----------------------------------------------------------------------------


class OutputFormat_Text_CSV(OutputFormatBase):
    """
    Output format for CSV writing.
    Options:
     - csv_header = "ids", "names", or "none".
     - dest = "filename" or "-" for STDOUT
     - dialect = "excel" or "excel-tab", ...
    """
    def __init__(self, options):
        OutputFormatBase.__init__(self, options)
        self._csvout = None
        self._csv_header = self._options.get('csv_header', None)
        self._dialect = self._options.get('dialect', 'excel')
    def open(self, tournament, entrants):
        """Abstract: Open and write header to output."""
        OutputFormatBase.open(self, tournament, entrants)
        self._open_file(self._dest)
        self._csvout = csv.writer(self._f, dialect=self._dialect)
        if self._options.get('csv_header', None):
            field_ids = []
            field_names = []
            for field in self._tournament.output.fields:
                field_ids += field.function.ids()
                field_names += field.function.names()
            if self._options.get('csv_header', False) == 'ids':
                self._csvout.writerow(field_ids)
            if self._options.get('csv_header', False) == 'names':
                self._csvout.writerow(field_names)
    def entrant(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Write results for single entrant to output."""
        vals = []
        for field in self._tournament.output.fields:
            fieldvals = field.function.execute(entrant_num, entrant, criteria, lens_data)
            vals += fieldvals
        self._csvout.writerow(vals)
    def close(self):
        """Abstract: Write footer to output and close."""
        self._close_file(self._dest)

class OutputFormat_Text_TSV(OutputFormat_Text_CSV):
    """
    Output format for CSV writing with tab separators.
    Same options as text_csv, but overrides dialect as "excel-tab".
    """
    def __init__(self, options):
        OutputFormat_Text_CSV.__init__(self, options)
        self._dialect = 'excel-tab'
        if 'tsv_header' in options:
            self.csv_header = options['tsv_header']

class OutputFormat_Text_JSON(OutputFormatBase):
    """
    Output format for JSON writing.
    """
    def __init__(self, options):
        OutputFormatBase.__init__(self, options)
        self._entrant_count = 0
    def open(self, tournament, entrants):
        """Abstract: Open and write header to output."""
        OutputFormatBase.open(self, tournament, entrants)
        self._open_file(self._dest)
        self._f.write("[\n")
    def entrant(self, entrant_num, entrant, criteria, lens_data):
        """Abstract: Write results for single entrant to output."""
        self._entrant_count += 1
        if self._entrant_count > 1:
            self._f.write(",")
            self._f.write("\n")
        entrant_data = dict()
        for field in self._tournament.output.fields:
            fieldvals = field.function.execute(entrant_num, entrant, criteria, lens_data)
            fieldids = field.function.ids()
            entrant_data.update(dict(zip(fieldids, fieldvals)))
        self._f.write("  ")
        self._f.write(json.dumps(entrant_data))
    def close(self):
        """Abstract: Write footer to output and close."""
        self._f.write("\n]\n")
        self._close_file(self._dest)

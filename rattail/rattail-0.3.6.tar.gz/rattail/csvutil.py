#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.csvutil`` -- CSV File Utilities

Contains various utilities relating to CSV file processing.

.. note::
   This module is named ``csvutil`` instead of ``csv`` primarily as a
   workaround to the problem of ``PythonService.exe`` insisting on doing
   relative imports.
"""

import csv
import codecs


class DictWriter(csv.DictWriter):
    """
    Convenience implementation of ``csv.DictWriter``.

    This exists only to provide the :meth:`writeheader()` method on Python 2.6.
    """

    def writeheader(self):
        if hasattr(csv.DictWriter, 'writeheader'):
            return csv.DictWriter.writeheader(self)
        self.writer.writerow(self.fieldnames)


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, fileobj, encoding):
        self.reader = codecs.getreader(encoding)(fileobj)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf_8')


class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in a CSV file, which is encoded
    in the given encoding.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, fileobj, dialect=csv.excel, encoding='utf_8', **kwargs):
        fileobj = UTF8Recoder(fileobj, encoding)
        self.reader = csv.reader(fileobj, dialect=dialect, **kwargs)

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        return [unicode(x, 'utf_8') for x in row]

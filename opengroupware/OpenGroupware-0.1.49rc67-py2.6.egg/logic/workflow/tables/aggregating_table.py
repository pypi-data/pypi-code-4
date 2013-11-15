#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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
#
import logging
from coils.foundation import BLOBManager
from coils.core import CoilsException
from table import Table


class AggregatingLookupTable(Table):
    _delimiter = ','  # delimiter to use when in "join" mode
    _mode = 'coalesce'  # mode: coalesce | join
    _chained_table_names = None  # List of chained table names
    _chained_tables = None  # List of instances of chained tables
    _chained_table_name = None  # Name of chained [fallback] table, if any
    _chained_table = None  # Instance of chained [fallback] table
    _default_value = None  # Default [fallback] return value

    def __init__(self, context=None, process=None, scope=None, ):
        """
        ctor

        :param context: Security and operation context for message lookup
        :param process: Proccess to use when resolving message lookup
        :param scope: Scope to use when resolving message lookup
        """

        Table.__init__(self, context=context, process=process, scope=scope, )
        self.log = logging.getLogger('OIE.AggregatingLookupTable')

    def __repr__(self):
        return '<AggregatingLookupTable name="{0}" />'.format(self.name, )

    def set_rfile(self, rfile):
        """
        Directly set the rfile attribute.

        :param rfile: Provides the table with a file handle to read the
            document, this is used for testing (otherwise the table cannot
            execute outside of a process instance).
        """
        self._rfile = rfile

    def set_aggregation_mode(self, mode):
        if mode not in ('join', 'coalesce', ):
            raise CoilsException(
                'Unsupported Aggregation mode: "{0}"'.
                format(mode, ))
        self._mode = mode

    @property
    def aggregation_mode(self):
        return self._mode

    def set_description(self, description):
        """
        Load description of the table

        :param description: A dict describing the table
        """

        self.c = description
        self._name = self.c.get('name', None)
        self.set_aggregation_mode(self.c.get('mode', 'coalesce'))
        self._delimiter = self.c.get('delimiter', ',')

        chained_tables = self.c.get('chainedTables', None)
        if not chained_tables:
            raise CoilsException(
                'No "chainedTables" specified in table description'
            )
        if not isinstance(chained_tables, list):
            raise CoilsException(
                '"chainedTables" must be type <list>, is type "{0}"'.
                format(type(chained_tables, ))
            )
        self._chained_table_names = chained_tables

        self._chained_table_name = self.c.get('chainedTable', None)
        self._default_value = self.c.get('default_value', None)

    def add_table(self, table):
        if not self._chained_tables:
            self._chained_tables = list()
        self._chained_tables.append(table)

    def load_tables(self):
        if not self._chained_tables:
            for table_name in self._chained_table_names:
                table = Table.Load(table_name)
                table.setup(
                    context=self._context,
                    process=self._process,
                    scope=self._scope, )
                self.add_table(table)

    def _fallback_return(self, *values):
        self.log.debug(
            'Table "{0}" checking for fallback return value'.
            format(self.name, )
        )
        if self._chained_table_name and not self._chained_table:
            self._chained_table = Table.Load(self._chained_table_name)
            if not self._chained_table:
                raise CoilsException(
                    'Unable to marshall specified chainedTable: {0}'.
                    format(self._chained_table, ))
            else:
                self._chained_table.setup(
                    context=self._context,
                    process=self._process,
                    scope=self._scope, )
        if self._chained_table:
            self.log.debug(
                        'Table "{0}" Interrogating chained table "{1}"'.
                        format(self.name, self._chained_table_name, )
                    )
            return self._chained_table.lookup_value(*values)
        if self._default_value:
            self.log.debug(
                        'Table "{0}" returning default value'
                    )
            return self._default_value
        return None

    def lookup_value(self, *values):
        """
        Perform XPath lookup into referenced document.

        :param values: list of values to load into the XPath
        """

        if not values:
            return None

        self.load_tables()

        if self._mode == 'coalesce':
            result = None
            for table in self._chained_tables:
                result = table.lookup_value(*values)
                if result:
                    break
            return result
        elif self._mode == 'join':
            result = list()
            for table in self._chained_tables:
                tmp = table.lookup_value(*values)
                if tmp:
                    result.append(tmp)
            if result:
                return self._delimiter.join(result)

        return self._fallback_return(*values)

    def shutdown(self):
        """
        Tear down any externally referenced resources
        """

        Table.shutdown(self)
        self._xmldoc = None

#
# Copyright (c) 2012, 2013
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
import inspect
import yaml
import uuid
from coils.foundation import BLOBManager
from coils.core import CoilsException
from table import Table
from lxml import etree

HARD_NAMESPACES = {
    'dsml': u'http://www.dsml.org/DSML',
    'apache': u'http://apache.org/dav/props',
    'caldav': u'urn:ietf:params:xml:ns:caldav',
    'carddav': u'urn:ietf:params:xml:ns:carddav',
    'coils': u'57c7fc84-3cea-417d-af54-b659eb87a046',
    'dav': u'dav',
    'xhtml': u'http://www.w3.org/1999/xhtml',
    'mswebdav': u'urn:schemas-microsoft-com',
}


class XPathLookupTable(Table):

    def __init__(self, context=None, process=None, scope=None, ):
        """
        ctor

        :param context: Security and operation context for message lookup
        :param process: Proccess to use when resolving message lookup
        :param scope: Scope to use when resolving message lookup
        """

        Table.__init__(self, context=context, process=process, scope=scope, )
        self._xmldoc = None
        self._xpath = None
        self._label = None
        self._rfile = None
        self._do_input_upper = False
        self._do_input_strip = False
        self._do_output_upper = False
        self._do_output_strip = False
        self.log = logging.getLogger('OIE.XPathLookupTable')

    def __repr__(self):
        return '<XPathLookupTable name="{0}" />'.format(self.name, )

    def _load_document(self):
        if not self._rfile:
            message = self.context.run_command('message::get',
                                               process=self._process,
                                               scope=self._scope,
                                               label=self._label, )
            if message:
                self.log.debug(
                    'Retrieved message labelled "{0}" in scope "{1}"'.
                    format(self._label, self._label, )
                )
                rfile = self.context.run_command('message::get-handle',
                                                 message=message, )
                self.log.debug(
                    'Opened handle for message text"'.
                    format(self._label, self._label, ))
                self._rfile = rfile
            else:
                raise CoilsException(
                    'No message labelled "{0}" found in scope "{0}" of '
                    'OGo#{2} [Process]'.
                    format(
                        self._label,
                        self._scope,
                        self._process.object_id,
                    )
                )

        if not self._xmldoc:
            doc = etree.parse(self._rfile)
            self.log.debug('Content of message parsed')
            nsm = doc.getroot().nsmap
            for ab, ns in HARD_NAMESPACES.items():
                if ab not in nsm:
                    nsm[ab] = ns

            self._xmldoc = doc
            self._ns_map = nsm

    def _fallback_return(self, *values):
        if self._chained_table:
            return self._chained_table.lookup_value(*values)
        elif self._default_value is not None:
            return self._default_value
        return None

    def _stringify_result(self, result):
        self.log.info('XPathLookupTable result: "{0}"'.format(result, ))
        if result:
            self.log.debug(
                'XPath evluated to {0} results'.
                format(len(result), ))
            result = result[0]
            if isinstance(result, basestring):
                self.log.debug('XPath result is type string')
                return result
            else:
                self.log.debug('XPath result is not a string')
                return etree.tostring(result)
        return None

    def set_rfile(self, rfile):
        """
        Directly set the rfile attribute.

        :param rfile: Provides the table with a file handle to read the
            document, this is used for testing (otherwise the table cannot
            execute outside of a process instance).
        """
        self._rfile = rfile

    def set_description(self, description):
        """
        Load description of the table

        :param description: A dict describing the table
        """

        self.c = description
        self._name = self.c.get('name', None)

        self._default_value = self.c.get('defaultValue', None)
        if self.c.get('chainedTable', None):
            self._chained_table = Table.Load(self.c['chainedTable'])
        else:
            self._chained_table = None

        self._xpath = self.c.get('XPath', None)
        if not self._xpath:
            raise CoilsException('No XPath defined for XPath lookup table')
        self._xpath = self._xpath.replace('"?"', '"{}"')

        self._label = self.c.get('messageLabel', None)
        if not self._label:
            raise CoilsException(
                'No message label defined for XPath lookup table')

    def lookup_value(self, *values):
        """
        Perform XPath lookup into referenced document.

        :param values: list of values to load into the XPath
        """

        if not values:
            return None

        self.log.debug(
            'XPath lookup requested via table "{0}" with values: {1}'.
            format(self.name, values, )
        )

        self._load_document()

        try:
            xp = self._xpath.format(*values)
        except IndexError as exc:
            self.log.error(
                'Incorrect sequence of parameters creating XPath '
                'query string for table {0}, parameters: {1}'.
                format(self.name, values))
            raise exc
        self.log.debug(
            'Performing XPath expression: {0}'.
            format(xp, )
        )

        try:
            result = self._xmldoc.xpath(xp, namespaces=self._ns_map, )
        except Exception as exc:
            self.log.error(
                'Error evaluating XPath expression {0} for table "{1}"'.
                format(xpath, self.name, )
            )
            self.log.exception(exc)
            raise exc

        if not result:
            self.log.debug(
                'XPath evaluated to None, '
                'returning values from fallback [if any]'
            )
            return self._fallback_return(*values)

        return self._stringify_result(result)

    def shutdown(self):
        """
        Tear down any externally referenced resources
        """

        if self._rfile:
            BLOBManager.Close(self._rfile)
        Table.shutdown(self)

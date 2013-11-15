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


class DSMLLookupTable(Table):
    _attr_filter = None  # List of attributes for XPath query
    _attr_path = None  # Path to desired return value
    _xmldoc = None  # Parsed XML document from DSML message
    _label = None  # Message label of DSML document
    _rfile = None  # File handle of DSML document
    _default_value = None  # Default [fallback] return value

    def __init__(self, context=None, process=None, scope=None, ):
        """
        ctor

        :param context: Security and operation context for message lookup
        :param process: Proccess to use when resolving message lookup
        :param scope: Scope to use when resolving message lookup
        """

        Table.__init__(self, context=context, process=process, scope=scope, )
        self.log = logging.getLogger('OIE.DSMLLookupTable')

    def __repr__(self):
        return '<DSMLLookupTable name="{0}" />'.format(self.name, )

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
        self._default_value = self.c.get('defaultValue', None)
        self._name = self.c.get('name', None)

        if self.c.get('chainedTable', None):
            self._chained_table = Table.Load(self.c['chainedTable'])
        else:
            self._chained_table = None

        self._attr_path = self.c.get('attributePath', None)
        if not self._attr_path:
            raise CoilsException(
                'No "AttributePath" defined for XPath lookup table'
            )
        if not isinstance(self._attr_path, basestring):
            raise CoilsException('"attributePath" must be type <string>')
        self._attr_path = self._attr_path.split('.')

        self._attr_filter = self.c.get('filterAttributes', None)
        if not self._attr_path:
            raise CoilsException('No FilterAttributes for XPath lookup table')
        if not isinstance(self._attr_filter, list):
            raise CoilsException('"filterAttributes" must be type <list>')

        self._label = self.c.get('messageLabel', None)
        if not self._label:
            raise CoilsException(
                'No message label defined for XPath lookup table')

        self.log.info(
            'DSMLLookupTable "{0}" initialized'.
            format(self._name, ))

    def _load_document(self):

        if self._xmldoc:
            return

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

        doc = etree.parse(self._rfile)
        self.log.debug('Content of message parsed')
        nsm = doc.getroot().nsmap
        for ab, ns in HARD_NAMESPACES.items():
            if ab not in nsm:
                nsm[ab] = ns

        self._xmldoc = doc
        self._ns_map = nsm

    @property
    def xml_document(self):
        return self._xmldoc

    @property
    def xml_namespaces(self):
        return self._ns_map

    def _make_filter_xpath(self, *values):
        xpath = '/dsml:dsml/dsml:directory-entries/dsml:entry/'
        for i in range(0, len(self._attr_filter)):
            xpath += \
                'dsml:attr[@name="{0}"]/dsml:value[text()="{1}"]/../../'.\
                format(self._attr_filter[i], values[i], )
        xpath += \
            'dsml:attr[@name="{0}"]/dsml:value/text()'.\
            format(self._attr_path[0], )
        xpath = xpath.format(values)
        self.log.debug(
            'Performing XPath expression: {0}'.
            format(xpath, )
        )
        return xpath

    def _make_forward_value_xpath(self, dn, attribute, ):
        xpath = \
            '/dsml:dsml/dsml:directory-entries/dsml:entry[@dn="{0}"]' \
            '/dsml:attr[@name="{1}"]/dsml:value[1]/text()'.\
            format(dn, attribute, )
        self.log.debug('Forward XPath is: {0}'.format(xpath, ))
        return xpath

    def _fallback_return(self, *values):
        if self._chained_table:
            return self._chained_table.lookup_value(*values)
        elif self._default_value is not None:
            return self._default_value
        return None

    def _stringify_result(self, result):
        self.log.info('DSMLLookupTable result: "{0}"'.format(result, ))
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

    def lookup_value(self, *values):
        """
        Perform XPath lookup into referenced document.

        :param values: list of values to load into the XPath
        """

        if not values:
            return None

        self.log.debug(
            'DSML lookup requested with values: {0}'.format(values, )
        )

        self._load_document()
        xpath = self._make_filter_xpath(*values)
        try:
            result = self._xmldoc.xpath(xpath, namespaces=self._ns_map, )
        except Exception as exc:
            self.log.error(
                'Error evaluating XPath expression {0} for table "{1}"'.
                format(xpath, self.name, )
            )
            self.log.exception(exc)
            raise exc

        if not result:
            return self._fallback_return(*values)
        if len(self._attr_path) == 1:
            return self._stringify_result(result)

        result = result[0]
        self.log.debug(
            'Attempting to follow attribute forward to "{0}"'.
            format(result, )
        )
        xpath = self._make_forward_value_xpath(
            dn=result,
            attribute=self._attr_path[1],
        )

        try:
            result = self._xmldoc.xpath(xpath, namespaces=self._ns_map, )
        except Exception as exc:
            self.log.error(
                'Error evaluating XPath expression {0} for table "{1}"'.
                format(xpath, self.name, )
            )
            self.log.exception(exc)

        if result is None:
            return self._fallback_return(*values)
        return self._stringify_result(result)

    def shutdown(self):
        """
        Tear down any externally referenced resources
        """

        if self._rfile:
            BLOBManager.Close(self._rfile)
        Table.shutdown(self)
        self._xmldoc = None

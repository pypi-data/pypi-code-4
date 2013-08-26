# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlreaders.utils`` module defines various classes and functions
used in the different specialized format readers.

It also defines the base class for the format readers, or functions to
read the addresses defined in an XML element inspired by the DocBook standard,
or dump adress objects into XML elements.

.. autoclass:: AccDocFormatAbstractReader
   :show-inheritance:

.. autofunction:: read_person_address

.. autofunction:: fill_address_from_address_block

.. autofunction:: read_text_from_xml_elt
"""
__docformat__ = "restructuredtext en"

from traceback import format_exc
from pybill.lib import PBD_XMLNS
from pybill.lib.errors import PyBillReadingException
from pybill.lib.entities.addresses import PersonAddress, OrganisationAddress
from datetime import date
import re


RE_DATE = re.compile("([\d]{4})-([\d]{2})-([\d]{2})[.]*")


class AccDocFormatAbstractReader:
    """
    Base class for the various specialized format readers. A format reader can
    read the XML data in a given format and build the corresponding accounting
    document.

    .. attribute:: filename

       Attribute containing the name of the file that the XML data is read
       from. This file name is mostly used when reporting errors.

       type: :class:`unicode`

    .. automethod:: __init__

    .. automethod:: read_accounting_doc

    .. automethod:: _select_from_xpaths

    .. automethod:: _read_number_from_xpaths

    .. automethod:: _read_date_from_xpaths

    .. automethod:: _read_text_from_xpaths
    """
    def __init__(self):
        """
        Initializes a new ``AccDocFormatAbstractReader`` object.

        As this class is abstract, raises an exception if the object class is
        not one of the child classes.
        """
        if self.__class__ is AccDocFormatAbstractReader:
            raise NotImplementedError("Abtract classes can't be instanciated")
        self.filename = u""

    def read_accounting_doc(self, xml_root, filename="", cfg=None):
        """
        Reads the data contained in the XML under the element
        ``xml_root`` and builds an accounting entity object.

        The class of the accounting entity object (``Bill``, ``ClaimForm``,
        ``Debit``, ``Downpayment``, ``ProForma``) depends on the data read in
        the XML.

        This abstract polymorphic method will be implemented in the child
        classes.
        
        :parameter xml_root: root element of the XML tree containing the
                             accounting document. The XML has already been
                             read with `lxml` parser.
        :type xml_root: :class:`lxml.etree.Element`
        
        :parameter filename: name of the file where the XML root element was
                             read from. This name is used to display nicest
                             errors.
        :type filename: :class:`unicode`

        :parameter cfg: Configuration object that might be useful for
                        format conversion. This object contains the
                        configuration read from a configuration XML file.
        :type cfg: :class:`~pybill.lib.config.entities.ConfigData`
        
        :returns: entity object containing the accounting document.
        :rtype: :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`
        """
        raise NotImplementedError()

    def _select_from_xpaths(self, xml_elt, xpaths):
        """
        Utilitary function that selects XML elements from an XPath pointer.

        More precisely, the XPath pointer is a list of several XPath that will
        be tried in the order of the list until one of them selects something.
        If none of them selects something, an empty result is returned.

        In the XPaths, you can use the ``pbd:`` prefix that is automatically
        binded to the PyBill document XML namespace (defined in
        :const:`PBD_XMLNS`).

        The result of the selection is returned as a list of XML nodes.

        :parameter xml_elt: XML element where the selection will be started
                            from (especially if the XPath are relative paths).
                            This element has been read in a file thanks
                            to `lxml` parser.
        :type xml_elt: :class:`lxml.etree.Element`

        :parameter xpaths: List of relative XPaths that points to the piece of
                           information that must be selected in the XML
                           element. If nothing is selected by the first XPath,
                           tries the second one, and so on until something is
                           selected.
        :type xpaths: :list of class:`unicode`

        :returns: List of XML nodes (element, attribute, text, etc.) selected
                  by one of the XPaths. If no piece of information was found,
                  returns an empty list.
        :rtype: list of :class:`object`
        """
        selection = []
        for xpath in xpaths:
            selection = xml_elt.xpath(xpath, namespaces={"pbd": PBD_XMLNS})
            if len(selection) > 0:
                break
        return selection

    def _read_number_from_xpaths(self, xml_elt, xpaths, converted_type,
                                 def_value=None, infoname=u""):
        """
        Utilitary function that reads a piece of information in an XML element
        and tries to convert it to a float or an integer.

        If the information doesn't exist, returns a default value. If several
        pieces of information exist, uses the first one. If there is an error
        during the numeric conversion, returns a nice error message.

        In the XPaths, you can use the ``pbd:`` prefix that is automatically
        binded to the PyBill document XML namespace (defined in
        :const:`PBD_XMLNS`).

        :parameter xml_elt: XML element where the piece of information will be
                            read. This element has been read in a file thanks
                            to `lxml` parser.
        :type xml_elt: :class:`lxml.etree.Element`

        :parameter xpaths: List of relative XPaths that points to the piece of
                           information that must be read in the XML element. If
                           nothing is selected by the first XPath, tries the
                           second one, and so on until something is selected.
        :type xpaths: :list of class:`unicode`

        :parameter converted_type: Type of number that the information must be
                                   converted to. Can be ``float`` or ``int``
        :type converted_type: :class:`type`

        :parameter def_value: Default value that is returned if the piece of
                              information can't be read in the XML element.
        :type def_value: :class:`float`

        :parameter infoname: Name of the information that must be read in the
                             XML element. Only used to display nice error
                             messages.
        :type infoname: :class:`unicode`

        :returns: Piece of information read in the XML element and converted to
                  a float or an integer. If no piece of information was found,
                  returns the default value.
        :rtype: :class:`float`
        """
        xml_info = self._select_from_xpaths(xml_elt, xpaths)
        if len(xml_info) == 0:
            return def_value
        try:
            info = converted_type(xml_info[0])
        except ValueError:
            if converted_type is float:
                str_type = u"float"
            elif converted_type is int:
                str_type = u"int"
            else:
                str_type = str(converted_type)
            raise PyBillReadingException("Error while reading %s file, when "
                                         "trying to convert %s specification "
                                         "('%s') to %s."
                                         % (self.filename, infoname,
                                            unicode(xml_info[0]), str_type))
        return info

    def _read_date_from_xpaths(self, xml_elt, xpaths, infoname=u""):
        """
        Utilitary function that reads a piece of information in an XML element
        and tries to convert it to a date.

        If the information doesn't exist, returns ``None``. If several pieces
        of information exist, uses the first one. If there is an error in the
        conversion, returns a nice error message.

        In the XPaths, you can use the ``pbd:`` prefix that is automatically
        binded to the PyBill document XML namespace (defined in
        :const:`PBD_XMLNS`).

        :parameter xml_elt: XML element where the piece of information will be
                            read. This element has been read in a file thanks
                            to `lxml` parser.
        :type xml_elt: :class:`lxml.etree.Element`

        :parameter xpaths: List of relative XPaths that points to the piece of
                           information that must be read in the XML element. If
                           nothing is selected by the first XPath, tries the
                           second one, and so on until something is selected.
        :type xpaths: :list of class:`unicode`

        :parameter infoname: Name of the information that must be read in the
                             XML element. Only used to display nice error
                             messages.
        :type infoname: :class:`unicode`

        :returns: Piece of information read in the XML element and converted to
                  a date object. If no piece of information was found,
                  returns ``None``.
        :rtype: :class:`datetime.date`
        """
        xml_info = self._select_from_xpaths(xml_elt, xpaths)
        if len(xml_info) == 0:
            return None
        info = xml_info[0]
        try:
            assert RE_DATE.match(info)
            year, month, day = RE_DATE.match(info).groups()
            date_obj = date(int(year), int(month), int(day))
        except (AssertionError, ValueError), exc:
            msg = ("Error while reading %s file, when trying to convert %s "
                   "specification ('%s') to a date. Dates should be like "
                   "'CCYY-MM-DD'."
                   % (self.filename, infoname, unicode(info)))
            if exc.__class__ is ValueError:
                msg += "\n%s" % format_exc(limit=1)
            raise PyBillReadingException(msg)
        return date_obj

    def _read_text_from_xpaths(self, xml_elt, xpaths):
        """
        Utilitary function that reads a piece of information in an XML element
        and returns it as an unicode string.

        If the information doesn't exist, returns ``u""``. If several pieces of
        information exist, uses the first one.

        In the XPaths, you can use the ``pbd:`` prefix that is automatically
        binded to the PyBill document XML namespace (defined in
        :const:`PBD_XMLNS`).

        :parameter xml_elt: XML element where the piece of information will be
                            read. This element has been read in a file thanks
                            to `lxml` parser.
        :type xml_elt: :class:`lxml.etree.Element`

        :parameter xpaths: List of relative XPaths that points to the piece of
                           information that must be read in the XML element. If
                           nothing is selected by the first XPath, tries the
                           second one, and so on until something is selected.
        :type xpaths: :list of class:`unicode`

        :returns: Piece of information read in the XML element as an unicode
                  string. If no piece of information was found,
                  returns ``u""``.
        :rtype: :class:`unicode`
        """
        xml_info = self._select_from_xpaths(xml_elt, xpaths)
        if len(xml_info) == 0:
            return u""
        return unicode(xml_info[0])
 

#### Utilitary functions


def read_person_address(xml_addr, xml_ns=u""):
    """
    Utilitary function that reads an address defined in an XML element (\
    ``xml_addr``\ ) and stores it in an entity object.

    Hence, the XML defining an address was inspired by DocBook format and is the
    same in several PyBill formats and in the configuration files.

    :parameter xml_addr: XML element containing the definition of an
                         address in a DocBook-like format. This element
                         was read thanks to `lxml` parser.
    :type xml_addr: :class:`lxml.etree.Element`

    :parameter xml_ns: XML namespace where the XML address elements are
                       defined. Default value is ``u""`` (no namespace).
    :type xml_ns: :class:`unicode`

    :returns: An entity object storing the address information read from
              the XML element.
    :rtype: :class:`~pybill.lib.entities.addresses.PersonAddress`
    """
    addr = PersonAddress()
    addr.honorific = read_text_from_xml_elt(xml_addr,
                                             u"{%s}honorific" % xml_ns)
    addr.firstname = read_text_from_xml_elt(xml_addr, 
                                             u"{%s}firstname" % xml_ns)
    addr.other_name = read_text_from_xml_elt(xml_addr, 
                                              u"{%s}othername" % xml_ns)
    addr.surname = read_text_from_xml_elt(xml_addr, u"{%s}surname" % xml_ns)
    addr.lineage = read_text_from_xml_elt(xml_addr, u"{%s}lineage" % xml_ns)
    fill_address_from_address_block(addr, xml_addr, xml_ns)
    xml_aff = xml_addr.find(u"{%s}affiliation" % xml_ns)
    if xml_aff is not None:
        addr.organisation = OrganisationAddress()
        org = addr.organisation
        for jobtit in xml_aff.findall(u"{%s}jobtitle" % xml_ns):
            line = read_text_from_xml_elt(jobtit, u".")
            if line:
                org.job_titles.append(line)
        org.name = read_text_from_xml_elt(xml_aff, u"{%s}orgname" % xml_ns)
        for orgdiv in xml_aff.findall(u"{%s}orgdiv" % xml_ns):
            line = read_text_from_xml_elt(orgdiv, u".")
            if line:
                org.divisions.append(line)
        xml_org_addr = xml_aff.find(u"{%s}address" % xml_ns)
        if xml_org_addr is not None:
            fill_address_from_address_block(org, xml_org_addr, xml_ns)
    return addr


def fill_address_from_address_block(addr, xml_addr, xml_ns=u""):
    """
    Reads data from an address XML element and fills it in an address
    object.

    The XML defining an address was inspired by DocBook format.

    :parameter addr: An entity object that will be filled with the address
                     information read from the XML element. This object
                     can be a person address or an organisation address. It
                     is modified by this function.
    :type addr: :class:`~pybill.lib.entities.addresses.Address`

    :parameter xml_addr: XML element containing the definition of an
                         address in a DocBook-like format. This element
                         was read thanks to `lxml` parser.
    :type xml_addr: :class:`lxml.etree.Element`

    :parameter xml_ns: XML namespace where the XML address elements are
                       defined. Default value is ``u""`` (no namespace).
    :type xml_ns: :class:`unicode`
    """
    for street in xml_addr.findall(u"{%s}street" % xml_ns):
        line = read_text_from_xml_elt(street, u".")
        if line:
            addr.streets.append(line)
    addr.post_box = read_text_from_xml_elt(xml_addr, u"{%s}pob" % xml_ns)
    addr.post_code = read_text_from_xml_elt(xml_addr, u"{%s}postcode" % xml_ns)
    addr.city = read_text_from_xml_elt(xml_addr, u"{%s}city" % xml_ns)
    addr.state = read_text_from_xml_elt(xml_addr, u"{%s}state" % xml_ns)
    addr.country = read_text_from_xml_elt(xml_addr, u"{%s}country" % xml_ns)
    addr.phone = read_text_from_xml_elt(xml_addr, u"{%s}phone" % xml_ns)
    addr.fax = read_text_from_xml_elt(xml_addr, u"{%s}fax" % xml_ns)
    addr.web = read_text_from_xml_elt(xml_addr, u"{%s}web" % xml_ns)
    addr.email = read_text_from_xml_elt(xml_addr, u"{%s}email" % xml_ns)


def read_text_from_xml_elt(xml_startpoint, elt_name, def_value=u""):
    """
    Utilitary private function that returns the text contained in an
    XML element named ``elt_name`` selected from an XML start point.

    This function is mainly used by the functions reading the addresses from
    XML elements.

    :parameter xml_startpoint: XML element where the selection starts from.
    :type xml_addr: :class:`lxml.etree.Element`

    :parameter elt_name: Name of the XML element (most of the times, a 
                         child of the XML startpoint) containing the text we 
                         want to get. The name is given in ``lxml`` format:
                         ``{namespace}elt_name/{namespace}elt_name``.
    :type xpath: :class:`unicode`

    :parameter def_value: Default value to be returned if no XML element is
                          selected with ``elt_name``.
    :type def_value: :class:`unicode`

    :returns: The text contained in the XML element selected by ``elt_name`` 
              from ``xml_startpoint`` element. If the XML element is empty, 
              returns ``u""``. If the XML element doesn't exist, returns
              ``def_value``.
    :rtype: :class:`unicode`
    """
    xml_elt = xml_startpoint.find(elt_name)
    if xml_elt is None:
        return def_value
    text = xml_elt.findtext(u".")
    if text is None:
        return u""
    else:
        return unicode(text)

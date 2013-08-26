# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlwriters.utils`` module defines constants and common functions
used to write accounting entities in XML.

These functions mainly concern opening an XML file and writing an address object
into an XML element with a DocBook-like structure.

This module defines a constant that will be widely used in PyBill.

.. autodata:: ENCODING

It also defines the following utilitary functions.

.. autofunction:: open_xml_outfile

.. autofunction::  build_address_xml_element

.. autofunction:: write_address_xml_elements
"""
__docformat__ = "restructuredtext en"

from traceback import format_exc
from lxml import etree

from pybill.lib.errors import PyBillWritingException
from pybill.lib import PBD_XMLNS


ENCODING = u"UTF-8"
"""
Constant specifying the default encoding used for the XML files written in 
this package.

type: :class:`unicode`
"""


def open_xml_outfile(xml_file, encoding=ENCODING):
    """
    Opens an XML file in write mode, and writes the XML declaration.

    :parameter xml_file: Name of the XML file. Also works if this parameter
                         is an opened file.
    :type xml_file: :class:`unicode`

    :parameter encoding: Encoding used to write the XML file.
    :type encoding: :class:`str`

    :returns: opened file in write mode where the XML declaration has already
              been written.
    :rtype: :class:`file`
    """
    if type(xml_file) in (str, unicode):
        # xml_file is a string, thus a real filename, we try to open the file.
        try:
            out = open(xml_file, "w")
        except IOError, exc:
            raise PyBillWritingException("Can't open the '%s' file for writing "
                                   "data\n%s" % (xml_file, format_exc(limit=1)))
    else:
        # xml_file is not a string, we suppose it is an already opened file.
        out = xml_file
    # Writes the XML declaration in the file
    try:
        out.write('<?xml version="1.0" encoding="%s"?>\n\n' % encoding)
    except IOError, exc:
        raise PyBillWritingException("Can't write data in '%s' file\n%s"
                                     % (xml_file, format_exc(limit=1)))
    return out


def build_address_xml_element(address, xml_ns=u""):
    """
    Transforms the address object in an XML element whose structure is inspired
    by DocBook.

    This type of XML element is used in several PyBill formats (\
    `PyBill Document 0.X` or `PyBill Document 1.0`\ ). The XML element is built
    thanks to :mod:`lxml` library.

    :parameter address: Address object to be turned into an XML element.
    :type address: :class:`~pybill.lib.entities.addresses.PersonAddress`

    :parameter xml_ns: XML namespace where the address XML elements will be
                       defined in. The default value ``u""`` corresponds to
                       an empty namespace.
    :type xml_ns: :class:`unicode`
    
    :returns: An XML element built with `lxml` library that contains the
              information from the ``address`` object.
    :rtype: `:class:lxml.etree.Element`
    """
    adr_elt = etree.Element(u"{%s}address" % xml_ns)
    if address.honorific.strip() != u"":
        hnr_elt = etree.SubElement(adr_elt, u"{%s}honorific" % xml_ns)
        hnr_elt.text = address.honorific
    if address.firstname.strip() != u"":
        fnm_elt = etree.SubElement(adr_elt, u"{%s}firstname" % xml_ns)
        fnm_elt.text = address.firstname
    if address.other_name.strip() != u"":
        onm_elt = etree.SubElement(adr_elt, u"{%s}othername" % xml_ns)
        onm_elt.text = address.other_name
    if address.surname.strip() != u"":
        snm_elt = etree.SubElement(adr_elt, u"{%s}surname" % xml_ns)
        snm_elt.text = address.surname
    if address.lineage.strip() != u"":
        lng_elt = etree.SubElement(adr_elt, u"{%s}lineage" % xml_ns)
        lng_elt.text = address.lineage
    write_address_xml_elements(address, adr_elt, xml_ns)
    if address.organisation is not None:
        org = address.organisation
        aff_elt = etree.SubElement(adr_elt, u"{%s}affiliation" % xml_ns)
        ogn_elt = etree.SubElement(aff_elt, u"{%s}orgname" % xml_ns)
        ogn_elt.text = org.name
        for odiv in [d for d in org.divisions if d.strip() != u""]:
            odv_elt = etree.SubElement(aff_elt, u"{%s}orgdiv" % xml_ns)
            odv_elt.text = odiv
        for jbtit in [j for j in org.job_titles if j.strip() != u""]:
            jbt_elt = etree.SubElement(aff_elt, u"{%s}jobtitle" % xml_ns)
            jbt_elt.text = jbtit
        org_adr_elt = etree.Element(u"{%s}address" % xml_ns)
        write_address_xml_elements(org, org_adr_elt, xml_ns)
        if org_adr_elt.getchildren() != []:
            aff_elt.append(org_adr_elt)
    return adr_elt


def write_address_xml_elements(address, xml_elt, xml_ns=u""):
    """
    Writes the elements of the ``address`` object inside the ``xml_elt``
    XML element, using a structure inspired by DocBook.

    This function can be used to dump the elements of a ``PersonAddress`` or
    an ``OrganisationAddress``. The dumped elements are ``street``,
    ``postcode``, etc. that are common to both addresses.
    
    :parameter address: Address object whose elements must be written
                        in XML into the XML element. This object is either
                        a ``PersonAddress`` or an ``OrganisationAddress``.
    :type address: :class:`~pybill.lib.entities.addresses.Address`

    :parameter xml_elt: XML element in which the XML elements representing
                        the address elements will be written. This XML
                        element is built with the `lxml` library and will be
                        modified by this function (addition of new child
                        elements).
    :type xml_elt: :class:`lxml.etree.Element`

    :parameter xml_ns: XML namespace where the address XML elements will be
                       defined in. The default value ``u""`` corresponds to
                       an empty namespace.
    :type xml_ns: :class:`unicode`
    """
    for street in [s for s in address.streets if s.strip() != u""]:
        str_elt = etree.SubElement(xml_elt, u"{%s}street" % xml_ns)
        str_elt.text = street
    if address.post_box.strip() != u"":
        pbx_elt = etree.SubElement(xml_elt, u"{%s}pob" % xml_ns)
        pbx_elt.text = address.post_box
    if address.post_code.strip() != u"":
        pcd_elt = etree.SubElement(xml_elt, u"{%s}postcode" % xml_ns)
        pcd_elt.text = address.post_code
    if address.city.strip() != u"":
        cty_elt = etree.SubElement(xml_elt, u"{%s}city" % xml_ns)
        cty_elt.text = address.city
    if address.state.strip() != u"":
        sta_elt = etree.SubElement(xml_elt, u"{%s}state" % xml_ns)
        sta_elt.text = address.state
    if address.country.strip() != u"":
        cnt_elt = etree.SubElement(xml_elt, u"{%s}country" % xml_ns)
        cnt_elt.text = address.country
    if address.phone.strip() != u"":
        phn_elt = etree.SubElement(xml_elt, u"{%s}phone" % xml_ns)
        phn_elt.text = address.phone
    if address.fax.strip() != u"":
        fax_elt = etree.SubElement(xml_elt, u"{%s}fax" % xml_ns)
        fax_elt.text = address.fax
    if address.web.strip() != u"":
        web_elt = etree.SubElement(xml_elt, u"{%s}web" % xml_ns)
        web_elt.text = address.web 
    if address.email.strip() != u"":
        eml_elt = etree.SubElement(xml_elt, u"{%s}email" % xml_ns)
        eml_elt.text = address.email

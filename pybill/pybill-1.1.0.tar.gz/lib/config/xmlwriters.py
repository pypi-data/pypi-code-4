# -*- coding: utf-8 -*-
"""
``pybill.lib.config.xmlwriters`` module contains the function used for writing
``ConfigData`` objects into XML files.

This dump operation uses the :mod:`lxml` library.

.. autofunction:: save_config
"""
__docformat__ = "restructuredtext en"

from lxml import etree

from pybill.lib import PBC_1_0, PBC_XMLNS

from pybill.lib.errors import PyBillWritingException
from pybill.lib.xmlwriters.utils import (ENCODING, open_xml_outfile,
                                         write_address_xml_elements)


def save_config(cfg_data, xml_file, encoding=ENCODING):
    """
    Saves the configuration data contained in the ``cfg_data`` object into the
    ``xml_file`` file.

    The ``lxml`` library is used to write the XML data.
        
    :parameter cfg_data: Configuration object to be saved in XML.
    :type cfg_data: :class:`~pybill.lib.config.entities.ConfigData`    

    :parameter xml_file: name of the XML file that will be written.
                         data. Actually, this name is built from the reference
                         of the configuration data.
    :type xml_file: :class:`unicode`

    :parameter encoding: Encoding used to write the XML file.
    :type encoding: :class:`str`
    """
    # Builds root element
    xml_root = etree.Element(u"{%s}config" % PBC_XMLNS,
                             nsmap={"pbc": PBC_XMLNS})
    xml_root.set(u"{%s}format-version" % PBC_XMLNS, PBC_1_0)
    xml_root.set(u"{%s}name" % PBC_XMLNS, cfg_data.name)
    # Writes the company data
    xml_cpy = etree.SubElement(xml_root, u"{%s}company" % PBC_XMLNS)
    if cfg_data.company_logo.strip() != u"":
        xml_clg = etree.SubElement(xml_cpy, u"{%s}logo-file" % PBC_XMLNS)
        xml_clg.text = unicode(cfg_data.company_logo)
    xml_cnm = etree.SubElement(xml_cpy, u"{%s}orgname" % PBC_XMLNS)
    xml_cnm.text = cfg_data.company_address.name
    xml_addr = etree.Element(u"{%s}address" % PBC_XMLNS)
    write_address_xml_elements(cfg_data.company_address, xml_addr,
                               xml_ns= PBC_XMLNS)
    if xml_addr.getchildren() != []:
        xml_cpy.append(xml_addr)
    # Writes the bank data
    xml_bkd = etree.SubElement(xml_root, u"{%s}bank-data" % PBC_XMLNS)
    for line in [bkl for bkl in cfg_data.bank_data_lines
                 if bkl.strip() != u""]:
        xml_lne = etree.SubElement(xml_bkd, u"{%s}line" % PBC_XMLNS)
        xml_lne.text = line
    # Writes the footer 
    xml_ftr = etree.SubElement(xml_root, u"{%s}footer" % PBC_XMLNS)
    for line in [ftl for ftl in cfg_data.footer_lines if ftl.strip() != u""]:
        xml_lne = etree.SubElement(xml_ftr, u"{%s}line" % PBC_XMLNS)
        xml_lne.text = line
    # Writes the agreement intro
    xml_agr = etree.SubElement(xml_root, u"{%s}agreement-intro" % PBC_XMLNS)
    for line in [agl for agl in cfg_data.agreement_intro_lines
                 if agl.strip() != u""]:
        xml_lne = etree.SubElement(xml_agr, u"{%s}line" % PBC_XMLNS)
        xml_lne.text = line
    # Writes the number separators
    xml_nsp = etree.SubElement(xml_root, u"{%s}number-separators" % PBC_XMLNS)
    for sep_kw in [u"sign", u"thousands", u"digits"]:
        if cfg_data.number_separators.has_key(sep_kw):
            xml_sep = etree.SubElement(xml_nsp, u"{%s}%s" % (PBC_XMLNS, sep_kw))
            xml_sep.text = cfg_data.number_separators[sep_kw]
    # Writes the localisation data
    xml_loc = etree.SubElement(xml_root, u"{%s}localisation" % PBC_XMLNS)
    for loc_kw in [u"colon", u"phone-kw", u"fax-kw", u"web-kw", u"email-kw",
                   u"doc-ref-kw", u"receiver-kw", u"sender-kw", u"on-date",
                   u"bill", u"claim-form", u"downpayment", u"debit",
                   u"pro-forma", u"number", u"dated", u"valid-until",
                   u"intro-detail", u"quantity", u"description", u"vat-rate",
                   u"unit-price", u"tf-unit-price", u"price", u"tf-price",
                   u"it-price", u"holdback-on", u"ita-est", u"total",
                   u"tf-total", u"vat-amount", u"it-total", u"including",
                   u"holdback", u"on-tf", u"on-vat", u"debit-total",
                   u"charged-downpayment", u"charged-on", u"issued-debit",
                   u"issued-on", u"to-be-paid", u"payment-terms",
                   u"to-bring-forward", u"carry-forward", u"your-ref-kw",
                   u"purch-ref-kw", u"supplier-ref-kw"]:
        xml_lcp = etree.SubElement(xml_loc, u"{%s}%s" % (PBC_XMLNS, loc_kw))
        xml_lcp.text = cfg_data.local_phrases.get(loc_kw, u"")
    # Finally, writes the XML elements.
    out = open_xml_outfile(xml_file, encoding=encoding)
    out.write(etree.tostring(xml_root, encoding=encoding, 
                             pretty_print=True, xml_declaration=False))

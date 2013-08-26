# -*- coding: utf-8 -*-
"""
``pybill.lib.config.xmlreaders`` module contains the function used for reading
config XML files.

This function uses the :mod:`lxml` library to read the XML data. The
information read from one XML file is stored in a
:class:`~pybill.lib.config.entities.ConfigData` object.

.. autofunction:: load_config
"""
__docformat__ = "restructuredtext en"

from traceback import format_exc
from lxml import etree

from pybill.lib import PBC_0_X, PBC_FORMATS, PBC_XMLNS

from pybill.lib.xmlreaders.utils import (fill_address_from_address_block,
                                         read_text_from_xml_elt)
from pybill.lib.errors import PyBillReadingException
from pybill.lib.config.entities import ConfigData


def load_config(xml_file):
    """
    Loads the configuration data contained in the file ``xml_file``, stores
    it in a ``ConfigData`` object, and returns the new object.

    The ``lxml`` library is used to read the data from the XML.
        
    :parameter xml_file: name of the XML file containing the configuration
                         data.
    :type xml_file: :class:`unicode`

    :returns: A new configuration object filled with the data read in the
              XML file.
    :rtype: :class:`~pybill.lib.config.entities.ConfigData`    
    """
    config_data = ConfigData()
    # Tries to read the XML file
    try:
        xml_tree = etree.parse(xml_file)
    except Exception, exc:
        raise PyBillReadingException("Error while reading configuration "
                               "file %s\n%s" % (xml_file, format_exc(limit=1)))
    xml_root = xml_tree.getroot()
    if xml_root.tag not in  [u"config", u"{%s}config" % PBC_XMLNS]:
        raise PyBillReadingException("%s file is not a PyBill "
                                     "configuration file." % xml_file)
    # Finds config format
    cfg_format = xml_root.get(u"{%s}format-version" % PBC_XMLNS)
    if cfg_format is None and u"format-version" not in xml_root.keys():
        cfg_format = PBC_0_X
    elif cfg_format is None:
        cfg_format = xml_root.get(u"format-version")
    if cfg_format not in PBC_FORMATS:
        raise PyBillReadingException("Configuration from '%s' file is not in a"
                          " PyBill known format: %r." % (xml_file, cfg_format))
    # Sets configuration name
    cfg_name = xml_root.get(u"{%s}name" % PBC_XMLNS)
    if cfg_name is None:
        cfg_name = xml_root.get(u"name", u"")
    config_data.name = cfg_name
    # Chooses the namespace depending on the config format
    if cfg_format == PBC_0_X:
        xml_ns = u""
    else:
        xml_ns = PBC_XMLNS
    # Reads the company data
    xml_cpy = xml_root.find(u"{%s}company" % xml_ns)
    if xml_cpy is not None:
        config_data.company_logo = read_text_from_xml_elt(xml_cpy,
                                                     u"{%s}logo-file" % xml_ns)
        addr = config_data.company_address
        addr.name = read_text_from_xml_elt(xml_cpy, u"{%s}orgname" % xml_ns)
        xml_addr = xml_cpy.find(u"{%s}address" % xml_ns)
        if xml_addr is not None:
            fill_address_from_address_block(addr, xml_addr, xml_ns=xml_ns)
    # Reads the bank data
    for xml_ln in xml_root.findall(u"{%s}bank-data/{%s}line"
                                                           % (xml_ns, xml_ns)):
        line = read_text_from_xml_elt(xml_ln, u".")
        if line:
            config_data.bank_data_lines.append(unicode(line))
    # Reads the footer 
    for xml_ln in xml_root.findall(u"{%s}footer/{%s}line" % (xml_ns, xml_ns)):
        line = read_text_from_xml_elt(xml_ln, u".")
        if line:
            config_data.footer_lines.append(unicode(line))
    # Reads the agreement intro
    for xml_ln in xml_root.findall(u"{%s}agreement-intro/{%s}line"
                                                           % (xml_ns, xml_ns)):
        line = read_text_from_xml_elt(xml_ln, u".")
        if line:
            config_data.agreement_intro_lines.append(unicode(line))
    # Reads the number separators
    for sep_kw in [u"sign", u"thousands", u"digits"]:
        sep_val = read_text_from_xml_elt(xml_root,
                    u"{%s}number-separators/{%s}%s" % (xml_ns, xml_ns, sep_kw))
        if sep_val:
            config_data.number_separators[sep_kw] = sep_val
    # Reads the localisation data
    for xml_kwd in xml_root.find(u"{%s}localisation" % xml_ns):
        if xml_kwd.text and isinstance(xml_kwd.tag, str):
            kwd = unicode(xml_kwd.tag).split("}")[-1]
            config_data.local_phrases[kwd] = unicode(xml_kwd.text)
    # Finally, returns the configuration object
    return config_data

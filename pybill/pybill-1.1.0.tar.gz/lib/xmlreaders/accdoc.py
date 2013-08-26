# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlreaders.utils`` module defines the public class used for reading
accounting XML files ans building the corresponding entity objects.

The XML files are read with :mod:`lxml` library. They contain an accounting
document that can be a bill, a claim form, a debit, a downpayment or a
pro-forma. The information read from these files is stored in ``Bill``,
``ClaimForm``, ``Debit``, ``Downpayment`` or ``ProForma`` objects.

.. autoclass:: AccDocXMLReader
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from traceback import format_exc
from lxml import etree
from logilab.common.xmlutils import parse_pi_data

from pybill.lib import PBD_0_X, PBD_1_0 
from pybill.lib.accounting import CLIENT, CLIENT_HOLDBACK, PRODUCT, VAT
from pybill.lib import PBD_XMLNS
from pybill.lib.errors import PyBillReadingException

from pybill.lib.xmlreaders.accdoc_format_1_0 import AccDocFormat_1_0_Reader
from pybill.lib.xmlreaders.accdoc_format_0_X import AccDocFormat_0_X_Reader


class AccDocXMLReader:
    """
    Class reading an XML file containing an accounting document.

    After opening the XML file thanks to `lxml` XML parser, this class
    finds a processing instruction that specifies the name of the configuration
    file to be used for turning the accounting document in PDF, instanciates a
    specialized reader object matching the format of the accounting document,
    and asks it to read the data. Then, it returns the entity object built by
    the specialized reader. This entity object is, eventually, linked to the
    configuration object.

    :ivar format_readers:
        Dictionary of specialized format readers that can read a given format of
        accounting document; these readers are indexed by the name of the format
        they can read. This dictionary contains all the specialized format
        readers supported by this reader.

    :type format_readers:
        dictionary of
        :class:`~pybill.lib.xmlreaders.utils.AccDocFormatAbstractReader` indexed
        by :class:`unicode` keys.

    :ivar cfg_register:
        Configuration register that returns a
        :class:`~pybill.lib.config.entities.ConfigData` object matching a
        configuration name. This register searches and reads the configuration
        file. If this file is not found, returns a default configuration
        object. The configuration is used here to convert accounting documents
        from older formats.

    :type cfg_register: :class:`~pybill.lib.config.register:ConfigRegister`

    .. automethod:: __init__
    """
    def __init__(self, config_register):
        """
        Initializes a new ``AccDocXMLReader`` object.

        :parameter config_register:
            Register containing the various configurations read by PyBill. This
            register is used to get the configuration used by the accounting
            documents read by this object (the configurations can be useful to
            convert data from older formats).
                                    
        :type config_register:
            :class:`~pybill.lib.config.register.ConfigRegister`
        """
        self.format_readers = {
            PBD_1_0: AccDocFormat_1_0_Reader(),
            PBD_0_X: AccDocFormat_0_X_Reader(),
                              }
        self.cfg_register = config_register

    def load_data(self, xml_file, config_ref=None):
        """
        Loads the accounting document contained in the file ``xml_file``.

        If the accounting document contains a pybill processing instruction
        giving the name of the configuration file to be used for document
        transformation in PDF, reads it and linkks it to the accounting entity.
        
        :parameter xml_file: name of the XML file containing the accounting
                             document to be read.
        :type xml_file: :class:`unicode`
        
        :parameter config_ref: reference of the XML configuration file that
                               has been manually specified and that will
                               override any configuration specification in the
                               accounting document.
        :type config_ref: :class:`unicode`
        
        :returns: the entity object containing the accounting document. This
                  object contains also a link towards the configuration object
                  that shall be used for its further process.
        :rtype: :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`
        """
        try:
            xml_tree = etree.parse(xml_file)
        except Exception, exc:
            raise PyBillReadingException("Error while reading accounting "
                                         "document from file %s\n%s"
                                         % (xml_file, format_exc(limit=1)))
        if config_ref is None:
            # Tries to find the reference of the configuration in a `pybill`
            # processing instruction.
            xml_pis = xml_tree.xpath(u"//processing-instruction('pybill')")
            for xml_pi in xml_pis:
                data = parse_pi_data(xml_pi.text)
                if data.has_key(u"config"):
                    config_ref = unicode(data[u"config"])
                    break
        cfg = self.cfg_register.get_config(config_ref)
        # Tries to find information about accounting accounts in a dedicated
        # processing instruction
        xml_pis = xml_tree.xpath(u"//processing-instruction('accounts')")
        accounts = {}
        if len(xml_pis) > 0:
            data = parse_pi_data(xml_pis[0].text)
            if data.has_key(u"client") and data[u"client"].strip() != u"":
                accounts[CLIENT] = data[u"client"].strip()
            if (data.has_key(u"client-holdback")
                and data[u"client-holdback"].strip() != u""):
                accounts[CLIENT_HOLDBACK] = data[u"client-holdback"].strip()
            if data.has_key(u"product") and data[u"product"].strip() != u"":
                accounts[PRODUCT] = data[u"product"].strip()
            if data.has_key(u"vat") and data[u"vat"].strip() != u"":
                accounts[VAT] = data[u"vat"].strip()
        # Reads the beginning of the document to guess the format and use
        # the proper specialized reader
        xml_root = xml_tree.getroot()
        doc_format = xml_root.get(u"{%s}format-version" % PBD_XMLNS, None)
        if doc_format is None:
            doc_format = xml_root.get(u"format-version", None)
        if (doc_format is None
            and xml_root.tag in [u"bill", u"claim-form", u"debit",
                                 u"downpayment", u"pro-forma"]):
            doc_format = PBD_0_X
        try:
            reader = self.format_readers[doc_format]
        except KeyError:
            raise PyBillReadingException("Document from %s file is not in a "
                                         "PyBill known format" % xml_file)
        # Reads the accounting document data, thanks to the proper reader.
        acc_doc = reader.read_accounting_doc(xml_root, xml_file, cfg)
        acc_doc.cfg_data = cfg
        acc_doc.account_numbers = accounts
        return acc_doc

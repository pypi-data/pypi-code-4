# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlreaders.accdoc_format_0_X`` module defines the specialized
format reader used to build an accounting document from XML data in
`PyBill Document 0.X` format.

The `PyBill Document 0.X` format is the format of the oldest versions of PyBill.

.. autoclass:: AccDocFormat_0_X_Reader
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import PBD_0_X
from pybill.lib.errors import PyBillReadingException

from pybill.lib.xmlreaders.utils import (AccDocFormatAbstractReader,
                                         read_person_address)

from pybill.lib.entities.accounting_docs import (Bill, ClaimForm, Downpayment,
                                                 ProForma, Debit)
from pybill.lib.entities.accounting_docs import AccItem, PreviousAccountingDoc


ACC_CLASSES = {u"bill": Bill,
               u"claim-form":ClaimForm,
               u"debit": Debit,
               u"downpayment": Downpayment,
               u"pro-forma": ProForma}


class AccDocFormat_0_X_Reader(AccDocFormatAbstractReader):
    """
    Class reading the XML data contained in an accounting document in
    `PyBill Document 0.X` format.

    This class instanciates and fills the accounting object corresponding to the
    document described in the XML data.

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes a new `AccDocFormat_0_X_Reader` object.
        """
        AccDocFormatAbstractReader.__init__(self)
    
    def read_accounting_doc(self, xml_root, filename="", cfg=None):
        """
        Reads the data contained in the XML and builds an accounting object.
        
        The class of the object (``Bill``, ``ClaimForm``, ``Debit``,
        ``Downpayment``, or ``ProForma``) depends on the data contained in the
        XML.
        
        :parameter xml_root: root element of the XML tree containing the
                             accounting document. The XML has already been
                             read with `lxml` parser.
        :type xml_root: :class:`lxml.etree.Element`

        :parameter filename: name of the file the XML root element was read
                             from. This name is used to display nicest errors.
        :type filename: :class:`unicode`

        :parameter cfg: Configuration object that is useful for converting the
                        data in 0.X format.
        :type cfg: :class:`~pybill.lib.config.entities.ConfigData`
        
        :returns: entity object containing the accounting document.
        :rtype: :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`
        """
        self.filename = filename
        # The type is the local name of the root element (without namespace)
        accdoc_type = unicode(xml_root.tag[(xml_root.tag.find('}'))+1:])
        if accdoc_type not in ACC_CLASSES:
            raise PyBillReadingException("Unknown type ('%s') of accounting "
                                         "document in %s file."
                                         %(accdoc_type, self.filename))
        if accdoc_type in [u"pro-forma"]:
            acc_doc = ACC_CLASSES[accdoc_type]()
        else:
            acc_doc = ACC_CLASSES[accdoc_type](
                                 self._read_text_from_xpaths(xml_root, [u"@id"])
                                               )
        # Reading metadata
        acc_doc.origin_format = PBD_0_X
        acc_doc.doc_ref = self._read_text_from_xpaths(xml_root, [u"@our-ref"])
        acc_doc.date = self._read_text_from_xpaths(xml_root, [u"@date"])
        acc_doc.place = self._read_text_from_xpaths(xml_root, [u"@place"])
        for old_kw in [u"your-ref", u"purch-ref", u"supplier-ref"]:
            val = self._select_from_xpaths(xml_root, ["@%s" % old_kw])
            if len(val) > 0:
                if cfg is None:
                    kw_name = old_kw
                else:
                    kw_name = cfg.get_local_phrase(u"%s-kw" % old_kw)
                acc_doc.other_infos[kw_name] = unicode(val[0])
        # Reading adresses
        xml_sender_addrs = self._select_from_xpaths(xml_root,
                                                   [u"address[@role='from']"])
        if len(xml_sender_addrs) > 0:
            acc_doc.sender = read_person_address(xml_sender_addrs[0])
        xml_receiver_addrs = self._select_from_xpaths(xml_root,
                                                      [u"address[@role='to']"])
        if len(xml_receiver_addrs) > 0:
            acc_doc.receiver = read_person_address(xml_receiver_addrs[0])
        else:
            raise PyBillReadingException("Can't find receiver of accounting "
                                         "document in %s file whereas this "
                                         "piece of data is mandatory." 
                                         % self.filename)
        # Reading remarks
        for rmk in self._select_from_xpaths(xml_root, [u"remark"]):
            rem = self._read_text_from_xpaths(rmk, [u"text()"])
            if rem:
                acc_doc.remarks.append(rem)
        # Reading items list
        for xml_item in self._select_from_xpaths(xml_root, [u"selling/item"]):
            item = AccItem()
            item.quantity = self._read_number_from_xpaths(xml_item,
                                      [u"qty/text()"], float, 0.0, u"quantity")
            item.quantity_digits = 1
            item.title = self._read_text_from_xpaths(xml_item,
                                                 [u"description/title/text()"])
            for dtl in self._select_from_xpaths(xml_item,
                                                [u"description/detail"]):
                detail = self._read_text_from_xpaths(dtl, [u"text()"])
                if detail:
                    item.details.append(detail)
            item.unit_price = self._read_number_from_xpaths(xml_item,
                             [u"unit-price/text()"], float, 0.0, u"unit price")
            if (accdoc_type == u"debit" and
                unicode(xml_root.get(u"with-vat")) == u"no"):
                item.vat_rate = None
            else:
                item.vat_rate = self._read_number_from_xpaths(xml_item,
                                     [u"vat/text()"], float, 19.6, u"VAT rate")
            item.holdback_rate =  None
            item.holdback_on_vat = False
            acc_doc.acc_items.append(item)
        # Reading payment terms (for all the types except pro-forma and debit)
        if accdoc_type in [u"bill", u"claim-form", u"downpayment"]:
            acc_doc.payment_terms = self._read_text_from_xpaths(xml_root,
                                                     [u"payment-terms/text()"])
        # Reading charged downpayment (bill specific info)
        if accdoc_type == u"bill":
            for xml_chgdwp in self._select_from_xpaths(xml_root,
                                                     [u"charged-downpayment"]):
                chgdwp = PreviousAccountingDoc()
                chgdwp.total = self._read_number_from_xpaths(xml_chgdwp,
                        [u"text()"], float, 0.0, u"charged downpayment amount")
                chgdwp.accdoc_id = self._read_text_from_xpaths(xml_chgdwp,
                                                               [u"@bill-id"])
                chgdwp.accdoc_date = self._read_text_from_xpaths(xml_chgdwp,
                                                               [u"@bill-date"])
                acc_doc.charged_downpayments.append(chgdwp)
        # Reading issued debits (bill specific info)
        if accdoc_type == u"bill":
            for xml_issdbt in self._select_from_xpaths(xml_root,
                                                       [u"issued-debit"]):
                issdbt = PreviousAccountingDoc()
                issdbt.total = self._read_number_from_xpaths(xml_issdbt,
                               [u"text()"], float, 0.0, u"issued debit amount")
                issdbt.accdoc_id = self._read_text_from_xpaths(xml_issdbt,
                                                               [u"@debit-id"])
                issdbt.accdoc_date = self._read_text_from_xpaths(xml_issdbt,
                                                              [u"@debit-date"])
                acc_doc.issued_debits.append(issdbt)
        # Reading downpayment percent (downpayment specific info)
        if accdoc_type == u"downpayment":
            acc_doc.percent = self._read_number_from_xpaths(xml_root,
                            [u"@percent"], float, 30.0, u"downpayment percent")
        # Reading validity date (pro-forma specific info)
        if accdoc_type == u"pro-forma":
            acc_doc.validity_date = self._read_text_from_xpaths(xml_root,
                                                           [u"@validity-date"])
        # Returns filled accounting document
        return acc_doc

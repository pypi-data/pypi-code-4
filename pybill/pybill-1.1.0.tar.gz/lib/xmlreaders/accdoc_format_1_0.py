# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlreaders.accdoc_format_1_0`` module defines the specialized
format reader used to build an accounting document from XML data in
`PyBill Document 1.0` format.

.. autoclass:: AccDocFormat_1_0_Reader
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY, PBD_1_0, PBD_XMLNS
from pybill.lib.errors import PyBillReadingException

from pybill.lib.xmlreaders.utils import (AccDocFormatAbstractReader,
                                         read_person_address)

from pybill.lib.entities.accounting_docs import (Bill, ClaimForm, Downpayment,
                                                 ProForma, Debit)
from pybill.lib.entities.accounting_docs import AccItem, PreviousAccountingDoc


ACC_CLASSES = {u"bill": Bill,
               u"claim-form": ClaimForm,
               u"debit": Debit,
               u"downpayment": Downpayment,
               u"pro-forma": ProForma}


class AccDocFormat_1_0_Reader(AccDocFormatAbstractReader):
    """
    Class reading the XML data contained in an accounting document in
    `PyBill Document 1.0` format.

    This class instanciates and fills the accounting object corresponding to the
    document described in the XML data.

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes a new ``AccDocFormat_1_0_Reader`` object.
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

        :parameter cfg: Configuration object that might be useful for
                        format conversion. For reading format `PDB-1.0`, the
                        configuration object is not needed.
        :type cfg: :class:`~pybill.lib.config.entities.ConfigData`
        
        :returns: entity object containing the accounting document.
        :rtype: :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`
        """
        self.filename = filename
        accdoc_type = self._read_text_from_xpaths(xml_root,
                                                  [u"@pbd:type", u"@type"])
        if accdoc_type not in ACC_CLASSES:
            raise PyBillReadingException("Unknown type ('%s') of accounting "
                                         "document in %s file."
                                         %(accdoc_type, self.filename))
        if accdoc_type in [u"pro-forma"]:
            acc_doc = ACC_CLASSES[accdoc_type]()
        else:
            acc_doc = ACC_CLASSES[accdoc_type](
                  self._read_text_from_xpaths(xml_root,
                                              [u"pbd:metadata/pbd:id/text()"]))
        # Reading metadata
        acc_doc.origin_format = PBD_1_0
        acc_doc.doc_ref = self._read_text_from_xpaths(xml_root,
                                          [u"pbd:metadata/pbd:doc-ref/text()"])
        acc_doc.date = self._read_text_from_xpaths(xml_root,
                                             [u"pbd:metadata/pbd:date/text()"])
        acc_doc.date_num = self._read_date_from_xpaths(xml_root,
                                            [u"pbd:metadata/pbd:date/@pbd:num",
                                             u"pbd:metadata/pbd:date/@num"],
                                            u"document standard date number")
        acc_doc.place = self._read_text_from_xpaths(xml_root,
                                            [u"pbd:metadata/pbd:place/text()"])
        for xml_info in self._select_from_xpaths(xml_root,
                                                 [u"pbd:metadata/pbd:info"]):
            xml_kw = self._read_text_from_xpaths(xml_info,
                                                 [u"@pbd:name", u"@name"])
            if xml_kw != u"":
                acc_doc.other_infos[xml_kw] = \
                             self._read_text_from_xpaths(xml_info, [u"text()"])
        # Reading adresses
        xml_sender_addrs = self._select_from_xpaths(xml_root,
                                             [u"pbd:address[@pbd:role='from']",
                                              u"pbd:address[@role='from']"])
        if len(xml_sender_addrs) > 0:
            acc_doc.sender = read_person_address(xml_sender_addrs[0],
                                                 xml_ns=PBD_XMLNS)
        xml_receiver_addrs = self._select_from_xpaths(xml_root,
                                               [u"pbd:address[@pbd:role='to']",
                                                u"pbd:address[@role='to']"])
        if len(xml_receiver_addrs) > 0:
            acc_doc.receiver = read_person_address(xml_receiver_addrs[0],
                                                   xml_ns=PBD_XMLNS)
        else:
            raise PyBillReadingException("Can't find receiver of accounting "
                                         "document in %s file whereas this "
                                         "piece of data is mandatory." 
                                         % self.filename)

        # Reading remarks
        for rmk in self._select_from_xpaths(xml_root, [u"pbd:remark"]):
            rem = self._read_text_from_xpaths(rmk, [u"text()"])
            if rem :
                acc_doc.remarks.append(rem)
        # Reading items list
        for xml_item in self._select_from_xpaths(xml_root,
                                                 [u"pbd:items-list/pbd:item"]):
            item = AccItem()
            item.quantity = self._read_number_from_xpaths(xml_item,
                                  [u"pbd:qty/text()"], float, 0.0, u"quantity")
            item.quantity_digits = self._read_number_from_xpaths(xml_item,
                                  [u"pbd:qty/@pbd:digits", u"pbd:qty/@digits"],
                                  int, 0, u"quantity digits")
            item.title = self._read_text_from_xpaths(xml_item,
                                         [u"pbd:description/pbd:title/text()"])
            for dtl in self._select_from_xpaths(xml_item,
                                              [u"pbd:description/pbd:detail"]):
                detail = self._read_text_from_xpaths(dtl, [u"text()"])
                if detail:
                    item.details.append(detail)
            item.unit_price = self._read_number_from_xpaths(xml_item,
                         [u"pbd:unit-price/text()"], float, 0.0, u"unit price")
            item.unit_price_digits = self._read_number_from_xpaths(xml_item,
                    [u"pbd:unit-price/@pbd:digits", u"pbd:unit-price/@digits"],
                    int, ACCURACY, u"unit price digits")
            item.vat_rate = self._read_number_from_xpaths(xml_item,
                            [u"pbd:vat-rate/text()"], float, None, u"VAT rate")
            item.holdback_rate =  self._read_number_from_xpaths(xml_item,
                                    [u"@pbd:holdback-rate", u"@holdback-rate"],
                                    float, None, u"holdback rate")
            hbk_on_vat = self._read_text_from_xpaths(xml_item,
                                [u"@pbd:holdback-on-vat", u"@holdback-on-vat"])
            item.holdback_on_vat = (hbk_on_vat.lower() == u"yes")
            acc_doc.acc_items.append(item)
        # Reading payment terms (for all the types except pro-forma and debit)
        if accdoc_type in [u"bill", u"claim-form", u"downpayment"]:
            acc_doc.payment_terms = self._read_text_from_xpaths(xml_root,
                                                 [u"pbd:payment-terms/text()"])
        # Reading charged downpayment and issued debits (bill specific infos)
        if accdoc_type == u"bill":
            for xml_elt_name, accdoc_list in \
                   [(u"pbd:charged-downpayment", acc_doc.charged_downpayments),
                    (u"pbd:issued-debit", acc_doc.issued_debits)]:
                for xml_elt in self._select_from_xpaths(xml_root,
                                                        [xml_elt_name]):
                    prev_doc = PreviousAccountingDoc()
                    prev_doc.total = self._read_number_from_xpaths(xml_elt,
                                 [u"@pbd:total", u"@total"], float, 0.0,
                                 u"%s total" % xml_elt_name.replace("-", " "))
                    prev_doc.vat_amount = self._read_number_from_xpaths(xml_elt,
                             [u"@pbd:vat", u"@vat"], float, 0.0,
                             u"%s vat amount" % xml_elt_name.replace("-", " "))
                    prev_doc.accdoc_id = self._read_text_from_xpaths(xml_elt,
                                                          [u"@pbd:id", u"@id"])
                    prev_doc.accdoc_date = self._read_text_from_xpaths(xml_elt,
                                                      [u"@pbd:date", u"@date"])
                    accdoc_list.append(prev_doc)
        # Reading downpayment percent (downpayment specific info)
        elif accdoc_type == u"downpayment":
            acc_doc.percent = self._read_number_from_xpaths(xml_root,
                                           [u"pbd:downpayment-percent/text()"],
                                           float, 30.0, u"downpayment percent")
        # Reading validity date (pro-forma specific info)
        elif accdoc_type == u"pro-forma":
            acc_doc.validity_date = self._read_text_from_xpaths(xml_root,
                                                 [u"pbd:validity-date/text()"])
        # Returns filled accounting document
        return acc_doc

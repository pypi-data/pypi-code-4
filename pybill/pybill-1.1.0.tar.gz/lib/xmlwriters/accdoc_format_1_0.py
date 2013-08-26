# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlwriters.accdoc_format_1_0`` module defines the function that
can write the accounting entities in an XML element in `PyBill Document 1.0`
format.

The function can write any accounting entities such as bills, claim-forms,
debits, downpayments, or pro-formas.

.. autofunction:: write_accdoc_1_0_xml
"""
__docformat__ = "restructuredtext en"

from lxml import etree

from pybill.lib import PBD_1_0, PBD_XMLNS
from pybill.lib.entities.accounting_docs import (Bill, ClaimForm, Debit,
                                                 Downpayment, ProForma)
from pybill.lib.xmlwriters.utils import build_address_xml_element

ACCDOC_TYPE = {Bill: u"bill",
               ClaimForm: u"claim-form",
               Debit: u"debit",
               Downpayment: u"downpayment",
               ProForma: u"pro-forma"}


def write_accdoc_1_0_xml(acc_doc):
    """
    Writes an accounting entity into an XML element in `PyBill Document 1.0`
    format.

    The XML element is built thanks to `lxml` library.
    
    :parameter acc_doc: PyBill entity describing the accounting document to
                        be turned in XML. Can be a ``Bill``, a ``ClaimForm``,
                        a ``Debit``, a ``Downpayment`` or a ``ProForma``
                        object.
    :type acc_doc: :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

    :returns: an XML element describing the accounting document in
              `PyBill Document 1.0` format.
    :rtype: :class:`lxml.etree.Element`
    """
    root_elt = etree.Element(u"{%s}accounting-document" % PBD_XMLNS,
                             nsmap={"pbd": PBD_XMLNS})
    root_elt.set(u"{%s}format-version" % PBD_XMLNS, PBD_1_0)
    root_elt.set(u"{%s}type" % PBD_XMLNS, ACCDOC_TYPE[acc_doc.__class__])
    # Downpayment percent (only for downpayments)
    if acc_doc.__class__ is Downpayment:
        dwp_elt = etree.SubElement(root_elt,
                                   u"{%s}downpayment-percent"  % PBD_XMLNS)
        dwp_elt.text = unicode(acc_doc.percent)
    # Validity date (only for pro-formas)
    if acc_doc.__class__ is ProForma:
        vld_elt = etree.SubElement(root_elt,
                                   u"{%s}validity-date" % PBD_XMLNS)
        vld_elt.text = acc_doc.validity_date
    # Metadata
    mtd_elt = etree.SubElement(root_elt, u"{%s}metadata" % PBD_XMLNS)
    if acc_doc.__class__ in [Bill, ClaimForm, Debit, Downpayment]:
        id_elt = etree.SubElement(mtd_elt, u"{%s}id" % PBD_XMLNS)
        id_elt.text = acc_doc.id
    drf_elt = etree.SubElement(mtd_elt, u"{%s}doc-ref" % PBD_XMLNS)
    drf_elt.text = acc_doc.doc_ref
    plc_elt = etree.SubElement(mtd_elt, u"{%s}place" % PBD_XMLNS)
    plc_elt.text = acc_doc.place
    dte_elt = etree.SubElement(mtd_elt, u"{%s}date" % PBD_XMLNS)
    dte_elt.text = acc_doc.date
    if acc_doc.date_num is not None:
        dte_elt.set(u"{%s}num" % PBD_XMLNS,
                    unicode(acc_doc.date_num.strftime("%Y-%m-%d")))
    other_kw = acc_doc.other_infos.keys()
    other_kw.sort() # Just to ease the tests
    for kw in other_kw:
        inf_elt = etree.SubElement(mtd_elt, u"{%s}info"  % PBD_XMLNS)
        inf_elt.set("{%s}name" % PBD_XMLNS, kw)
        inf_elt.text = acc_doc.other_infos[kw]
    # Sender address
    if acc_doc.sender is not None:
        sdr_elt = build_address_xml_element(acc_doc.sender, xml_ns= PBD_XMLNS)
        sdr_elt.set(u"{%s}role" % PBD_XMLNS, u"from")
        root_elt.append(sdr_elt)
    # Receiver address
    if acc_doc.receiver is not None:
        rcv_elt = build_address_xml_element(acc_doc.receiver ,xml_ns=PBD_XMLNS)
        rcv_elt.set(u"{%s}role" % PBD_XMLNS, u"to")
        root_elt.append(rcv_elt)
    # Remarks
    for rmk in [r for r in acc_doc.remarks if r.strip() != u""]:
        rmk_elt = etree.SubElement(root_elt, u"{%s}remark" % PBD_XMLNS)
        rmk_elt.text = rmk
    # Items list
    lst_elt = etree.SubElement(root_elt, u"{%s}items-list" % PBD_XMLNS)
    for acc_item in acc_doc.acc_items:
        itm_elt = etree.SubElement(lst_elt, u"{%s}item" % PBD_XMLNS)
        if acc_item.holdback_rate is not None:
            itm_elt.set(u"{%s}holdback-rate" % PBD_XMLNS,
                        unicode(acc_item.holdback_rate))
            if acc_item.holdback_on_vat:
                itm_elt.set(u"{%s}holdback-on-vat" % PBD_XMLNS, u"yes")
            else:
                itm_elt.set(u"{%s}holdback-on-vat" % PBD_XMLNS, u"no")
        qty_elt = etree.SubElement(itm_elt, u"{%s}qty" % PBD_XMLNS)
        qty_elt.set("{%s}digits" % PBD_XMLNS,
                    unicode(acc_item.quantity_digits))
        qty_elt.text = unicode(acc_item.quantity)
        desc_elt = etree.SubElement(itm_elt, u"{%s}description" % PBD_XMLNS)
        tit_elt = etree.SubElement(desc_elt, u"{%s}title" % PBD_XMLNS)
        tit_elt.text = acc_item.title
        for detail in [d for d in acc_item.details if d.strip() != u""]:
            dtl_elt = etree.SubElement(desc_elt, u"{%s}detail" % PBD_XMLNS)
            dtl_elt.text = detail
        upr_elt = etree.SubElement(itm_elt, u"{%s}unit-price" % PBD_XMLNS)
        upr_elt.set("{%s}digits" % PBD_XMLNS,
                    unicode(acc_item.unit_price_digits))
        upr_elt.text = unicode(acc_item.unit_price)
        if acc_item.vat_rate is not None:
            vtr_elt = etree.SubElement(itm_elt, u"{%s}vat-rate" % PBD_XMLNS)
            vtr_elt.text = unicode(acc_item.vat_rate)
    # Charged downpayment and issued debits (only for bills)
    if acc_doc.__class__ is Bill:
        for xml_elt_name, accdoc_list in \
                                      [(u"{%s}charged-downpayment" % PBD_XMLNS,
                                        acc_doc.charged_downpayments),
                                       (u"{%s}issued-debit" % PBD_XMLNS,
                                        acc_doc.issued_debits)]:
            for prev_doc in accdoc_list:
                pvd_elt = etree.SubElement(root_elt, xml_elt_name)
                pvd_elt.set(u"{%s}id" % PBD_XMLNS,
                            prev_doc.accdoc_id)
                pvd_elt.set(u"{%s}date" % PBD_XMLNS,
                            prev_doc.accdoc_date)
                pvd_elt.set(u"{%s}total" % PBD_XMLNS,
                            unicode(prev_doc.total))
                pvd_elt.set(u"{%s}vat" % PBD_XMLNS,
                            unicode(prev_doc.vat_amount))
    # Payment terms (only for bills, claim-forms, downpayments)
    if acc_doc.__class__ in [Bill, ClaimForm, Downpayment]:
        pmt_elt = etree.SubElement(root_elt, u"{%s}payment-terms" % PBD_XMLNS)
        pmt_elt.text = acc_doc.payment_terms
    # Finally returns the XML result
    return root_elt


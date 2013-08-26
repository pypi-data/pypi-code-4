# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.accounting_docs.bill`` module contains the definition
of the entity representing a bill.

.. autoclass:: Bill
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs.abstract import GenericAccountingDoc


class Bill(GenericAccountingDoc):
    """
    Entity class representing a bill.

    .. attribute:: charged_downpayments

       Attribute containing the list of the downpayments already charged in
       previous bills. The totals of these downpayments will be discarded from
       the total to be paid.

       type: list of :class:`~pybill.lib.entities.accounting_docs.utils.PreviousAccountingDoc`

    .. attribute:: issued_debits

       Attribute containing the list of the debits previously issued. The totals
       of these debits will be discarded from the total to be paid.

       type: list of :class:`~pybill.lib.entities.accounting_docs.utils.PreviousAccountingDoc`

    .. attribute:: payment_terms

       Attribute defining the description of the payment terms. This description
       will be displayed after the bank data that is read from the configuration
       file.
                         
       type: :class:`unicode`

    . automethod:: __init__
    """
    def __init__(self, bill_id):
        """
        Initializes an empty object.

        :parameter bill_id: Identifier of this accounting document.
        :type bill_id: :class:`unicode`
        """
        GenericAccountingDoc.__init__(self)
        self.charged_downpayments = []
        self.issued_debits = []
        self.payment_terms = u""
        # Filling the object with available data
        self.id = bill_id
        
    def get_downpayments_and_debits(self):
        """
        Computes the total of the already charged downpayments and the already
        issued debits.

        This total will be substracted at the end of the bill in order to
        compute the total to be paid.

        :returns: The total of downpayments and debits.
        :rtype: :class:`float`
        """
        total_dwp_dbt = 0.0
        for pad in (self.charged_downpayments + self.issued_debits):
            total_dwp_dbt += round(pad.total, ACCURACY)
        return round(total_dwp_dbt, ACCURACY)
            
    def get_to_be_paid_holdback_free(self):
        """
        Computes the total without holdback that must be paid.

        This total depends, of course, on the including taxes total but also on
        the holdbacks, the downpayments and the debits.
        
        :returns: The total without holdback of the bill that must be paid.
        :rtype: :class:`float`
        """
        total = self.get_including_taxes_total()
        total_dwp_dbt = self.get_downpayments_and_debits()
        total_hbk = self.get_holdback_amount() + self.get_holdback_vat_amount()
        if (total - total_hbk) >= total_dwp_dbt:
            return round(total - total_hbk - total_dwp_dbt, ACCURACY)
        else:
            return 0.0

    def get_to_be_paid_holdback(self):
        """
        Computes the total of holdbacks that must be paid.

        This total depends, of course, on the including taxes total but also on
        the holdbacks, the downpayments and the debits.
        
        :returns: The total of holdbacks of the bill that must be paid.
        :rtype: :class:`float`
        """
        total = self.get_including_taxes_total()
        total_dwp_dbt = self.get_downpayments_and_debits()
        total_hbk = self.get_holdback_amount() + self.get_holdback_vat_amount()
        if (total - total_hbk) >= total_dwp_dbt:
            return round(total_hbk, ACCURACY)
        else:
            return round(total_hbk - (total_dwp_dbt - (total - total_hbk)),
                         ACCURACY)

    def get_to_be_paid_vat(self):
        """
        Computes the total of VAT amounts that must be paid.

        This amount depends on the VAT amounts but also on the charged
        downpayments and the issued debits.

        :returns: The total of VAT amounts that must be paid.
        :rtype: :class:`float`
        """
        vat_amount = self.get_including_taxes_total() - self.get_price_total()
        prev_vats = [round(pad.vat_amount, ACCURACY) for pad
                     in (self.charged_downpayments + self.issued_debits)]
        vat_amount -= sum(prev_vats)
        return round(vat_amount, ACCURACY)

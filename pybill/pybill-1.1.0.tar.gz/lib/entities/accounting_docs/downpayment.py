# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.accounting_docs.downpayment`` module defines the entity
representing a downpayment.

.. autoclass:: Downpayment
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs.abstract import GenericAccountingDoc


class Downpayment(GenericAccountingDoc):
    """
    Entity class representing a downpayment

    .. attribute:: percent

       Attribute defining the percent of the total that must be paid as a
       downpayment. Hence, the downpayment represents a percent of the actual
       bill. By default, the percent is ``30.0``\ .

       type: :class:`float`

    .. attribute:: payment_terms

       Attribute defiing the description of the payment terms. This description
       will be displayed after the bank data that is read from the configuration
       file.
                         
       type: :class:`unicode`

    .. automethod:: __init__   
    """
    def __init__(self, downpay_id):
        """
        Initializes an empty object.

        :parameter downpay_id: Identifier of this accounting document.
        :type downpay_id: :class:`unicode`
        """
        GenericAccountingDoc.__init__(self)
        
        self.percent = 30.0
        self.payment_terms = u""
        # Filling the object with available data
        self.id = downpay_id

    def get_downpayment(self):
        """
        Computes the downpayment.

        The downpayment is the including taxes total multiplied by the
        downpayment percent.
        
        :returns: The amount of the downpayment.
        :rtype: :class:`float`
        """
        return round(self.get_including_taxes_total()
                     * round(self.percent, ACCURACY) / 100., ACCURACY)

    def get_to_be_paid_holdback_free(self):
        """
        Computes the total without holdback that must be paid.

        This total depends, of course, on the downpayment but also on the
        holdbacks.
        
        :returns: The total without holdback of the downpayment that must be
                  paid.
        :rtype: :class:`float`
        """
        total = self.get_including_taxes_total()
        total_dwp = self.get_downpayment()
        total_hbk = self.get_holdback_amount() + self.get_holdback_vat_amount()
        if total_dwp <= (total - total_hbk):
            return round(total_dwp, ACCURACY)
        else:
            return round(total - total_hbk, ACCURACY)

    def get_to_be_paid_holdback(self):
        """
        Computes the total of holdbacks that must be paid.

        This total depends, of course, on the downpayment but also on the
        holdbacks.
        
        :returns: The total of holdbacks of the downpayment that must be paid.
        :rtype: :class:`float`
        """
        total = self.get_including_taxes_total()
        total_dwp = self.get_downpayment()
        total_hbk = self.get_holdback_amount() + self.get_holdback_vat_amount()
        if total_dwp <= (total - total_hbk):
            return 0.0
        else:
            return round(total_dwp - (total - total_hbk), ACCURACY)

    def get_to_be_paid_vat(self):
        """
        Computes the total of VAT amounts that must be paid. This amount depends
        on the VAT amounts but also, of course, on the downpayment percent.

        :returns: The total of VAT amounts that must be paid.

        :rtype: :class:`float`
        """
        vat_amount = self.get_including_taxes_total() - self.get_price_total()
        return round(float(vat_amount * self.percent) / 100., ACCURACY)

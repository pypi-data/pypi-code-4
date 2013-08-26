# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.accounting_docs.claimform`` module defines the entity
representing a claim-form.

.. autoclass:: ClaimForm
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY
from pybill.lib.entities.accounting_docs.abstract import GenericAccountingDoc


class ClaimForm(GenericAccountingDoc):
    """
    Entity class representing a claim form.

    .. attribute:: payment_terms

       Attrribute defining the description of the payment terms. This
       description will be displayed after the bank data that is read from the
       configuration file.

       type: :class:`unicode`

    .. automethod:: __init__
    """
    def __init__(self, claim_id):
        """
        Initializes an empty object.

        :parameter claim_id: Identifier of this accounting document.
        :type claim_id: :class:`unicode`
        """
        GenericAccountingDoc.__init__(self)
        self.payment_terms = u""
        # Filling the object with available data
        self.id = claim_id

    def get_to_be_paid_holdback_free(self):
        """
        Computes the total without holdback that must be paid.

        This total depends, of course, on the including taxes total but also on
        the holdbacks.
        
        :returns: The total without holdback of the claim form that must be
                  paid.
        :rtype: :class:`float`
        """
        return round(self.get_including_taxes_total()
                     - self.get_holdback_amount()
                     - self.get_holdback_vat_amount(), ACCURACY)

    def get_to_be_paid_holdback(self):
        """
        Computes the total of holdbacks that must be paid.

        This total depends, of course, on the including taxes total but also on
        the holdbacks.
        
        :returns: The total of holdbacks of the claim form that must be paid.
        :rtype: :class:`float`
        """
        return round(self.get_holdback_amount()
                     + self.get_holdback_vat_amount(), ACCURACY)

    def get_to_be_paid_vat(self):
        """
        Computes the total of VAT amounts that must be paid.

        This amount depends on the VAT amounts.

        :returns: The total of VAT amounts that must be paid.
        :rtype: :class:`float`
        """
        vat_amount = self.get_including_taxes_total() - self.get_price_total()
        return round(vat_amount, ACCURACY)

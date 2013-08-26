# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.accounting_docs.debit`` module defines the entity
representing a debit.

.. autoclass:: Debit
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib.entities.accounting_docs.abstract import GenericAccountingDoc
from pybill.lib import ACCURACY


class Debit(GenericAccountingDoc):
    """
    Entity class representing a debit.

    Please note that, for this class, the `to_be_paid_*` methods give the
    amounts that must be paid back to the client.

    .. automethod:: __init__
    """
    def __init__(self, debit_id):
        """
        Initializes an empty object.

        :parameter debit_id: Identifier of this accounting document.
        :type debit_id: :class:`unicode`
        """
        GenericAccountingDoc.__init__(self)
        # Filling the object with available data
        self.id = debit_id

    def get_to_be_paid_holdback_free(self):
        """
        Computes the total without holdback that must be paid back to the
        client.

        This total depends, of course, on the including taxes total but also on
        the holdbacks.
        
        :returns: The total without holdback of the debit that must be
                  paid back to the client.
        :rtype: :class:`float`
        """
        return round(self.get_including_taxes_total()
                     - self.get_holdback_amount()
                     - self.get_holdback_vat_amount(), ACCURACY)

    def get_to_be_paid_holdback(self):
        """
        Computes the total of holdbacks that must be paid back to the client.

        This total depends, of course, on the including taxes total but also
        on the holdbacks.
        
        :returns: The total of holdbacks of the debit that must be paid back to
                  the client.
        :rtype: :class:`float`
        """
        return round(self.get_holdback_amount()
                     + self.get_holdback_vat_amount(), ACCURACY)

    def get_to_be_paid_vat(self):
        """
        Computes the total of VAT amounts that must be paid back to the client.

        This amount depends on the VAT amounts.

        :returns: The total of VAT amounts that must be paid back to the
                  client.
        :rtype: :class:`float`
        """
        vat_amount = self.get_including_taxes_total() - self.get_price_total()
        return round(vat_amount, ACCURACY)

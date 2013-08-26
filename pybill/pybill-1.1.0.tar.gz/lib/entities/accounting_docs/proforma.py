# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.accounting_docs.proforma`` module defines the entity
representing a pro-forma.

.. autoclass:: ProForma
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib.entities.accounting_docs.abstract import GenericAccountingDoc


class ProForma(GenericAccountingDoc):
    """
    Entity class representing a pro-forma bill used as a purchase order.

    .. attribute:: validity_date

       Attribute defining the date that the purchase order is valid until; this
       is a **string representation** of the date.

       type: :class:`unicode`

    .. automethod:: __init__
    """
    def __init__(self, prof_id=None):
        """
        Initializes an empty object.

        Please note that the objects of this class don't need an identifier. The
        identifier is kept in the arguments to have the same interface as the
        others accounting entities.

        :parameter prof_id: Just kept to have the same interface as the other
                            accounting entities. This identifier is not used as
                            ``ProForma`` objects don't have identifier.
        :type prof_id: :class:`unicode`
        """
        GenericAccountingDoc.__init__(self)        
        self.validity_date = ""
        # Filling the object with available data
        self.id = None

    def get_to_be_paid_holdback_free(self):
        """
        In a pro-forma, nothing is to be paid (it's not really a bill).

        This method always returns ``0.0``\ .
        
        :returns: ``0.0`` as nothing is to be paid.
        :rtype: :class:`float`
        """
        return 0.0

    def get_to_be_paid_holdback(self):
        """
        In a pro-forma, nothing is to be paid (it's not really a bill).

        This method always returns ``0.0``\ .
        
        :returns: ``0.0`` as nothing is to be paid.
        :rtype: :class:`float`
        """
        return 0.0

    def get_to_be_paid_vat(self):
        """
        In a pro-forma, nothing is to be paid (it's not really a bill).

        This method always returns ``0.0``\ .
        
        :returns: ``0.0`` as nothing is to be paid.
        :rtype: :class:`float`
        """
        return 0.0

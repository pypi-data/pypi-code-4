# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.accounting_docs.utils`` module defines some elementary
entities used by the entity classes.

.. autoclass:: AccItem
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: PreviousAccountingDoc
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY


class AccItem:
    """
    Entity class representing an item that appears on the accounting document.

    .. attribute:: quantity

       Attribute defining the quantity of the item. Is not necessarily an
       integer, can be a real.

       type: :class:`float`

    .. attribute:: quantity_digits

       Attribute defining the number of digits to be written, for the quantity,
       on the documents where the item is displayed. This number of digits is
       also used to round the quantity before doing any of the item computations
       (VAT, price, etc.) By default, the number of digits is ``0``.

       type: :class:`int`

    .. attribute:: title:

       Attribute containing the description of the item

       type: :class:`unicode`

    .. attribute:: details

       Attribute defining a list of additional descriptions of the item.

       type: list of :class:`unicode`

    .. attribute:: unit_price

       Attribute defining the unit price of the item. Actually, this is a tax
       free price.

       type: :class:`float`

    .. attribute:: vat_rate

       Attribute defining the VAT rate that is applied to this item. This rate
       is ``None`` when no VAT is applicable to the item. Default value is
       ``None``. The rate is expressed in percents (e.g. ``19.6`` for 19.6%).

       type: :class:`float`

    .. attribute:: holdback_rate

       Attribute defining the holdback rate applied to this item. Hence,
       sometimes, an holdback is retained from the price of the item (and will
       be billed a few months later after the item has been fully tested). Can
       be ``None`` if no holdback is applied to this item. Default value is
       ``None``. The rate is expressed in percents (e.g. ``5.0`` for 5.0%).

       type: :class:`float`

    .. attribute:: holdback_on_vat

       Attribute defining a flag set to ``True`` if the holdback is also applied
       on VAT (thus the holback will be computed and substracted from the tax
       free price and from the VAT amount). When set to ``False``, the holdback
       is only applied on the tax free price (therefore, we substract the
       holdback from the tax free price but we keep the integrality of the VAT
       amount).

       For example: if the tax free price is ``100.0``, the VAT rate is ``20.0``
       and the holdback rate is ``5.0``. If the holdback is on VAT, we will pay:
       ``100.0*(1.0-0.05) + 20.0*(1.0-0.05) = 114.0``.  If the holdback is not
       on VAT, we will pay: ``100.0*(1.0-0.05) +20.0 = 115.0``.

       By default, the holdback is not applied on VAT (flag set to ``False``).

       type: :class:`bool`

    .. automethod:: __init__   
    """
    def __init__(self):
        """
        Initializes an empty object.
        """    
        self.quantity = 0.0
        self.quantity_digits = 0
        self.title = u""
        self.details = []
        self.unit_price = 0.0
        self.unit_price_digits = ACCURACY
        self.vat_rate = None
        self.holdback_rate = None
        self.holdback_on_vat = False

    def get_price(self):
        """
        Computes the price of this item (\ ``quantity`` * ``unit_price``\ ).

        This price is actually a tax free price.
        
        :returns: The price of the item.
        :rtype: :class:`float`
        """
        return round(round(self.quantity, self.quantity_digits) *
                     round(self.unit_price, self.unit_price_digits), ACCURACY)

    def get_vat_amount(self):
        """
        Computes the Value Added Tax (VAT) amount for this item
        (\ ``price`` * ``vat_rate``\ ).

        When no VAT is defined for the item, returns ``0.0``.
        
        :returns: The VAT amount of the item. ``0.0`` if no VAT rate is defined
                  for the item.
        :rtype: :class:`float`
        """
        if self.vat_rate is None:
            return 0.0
        else:
            return round(self.get_price() *
                         (round(self.vat_rate, ACCURACY) / 100.), ACCURACY)

    def get_including_taxes_price(self):
        """
        Computes the including taxes price for this item (\ ``price`` +
        ``vat_amount``\ ).

        When no VAT is defined for the item, returns the tax free price (\
        ``price``\ ).
        
        :returns: The including taxes price of the item or the price of the item
                  if no VAT rate is defined for the item.
        :rtype: :class:`float`
        """
        if self.vat_rate is None:
            return self.get_price()
        else:
            return round(self.get_price() + self.get_vat_amount(), ACCURACY)

    def get_holdback_amount(self):
        """    
        Computes the holdback amount for this item (\ ``price`` *
        ``holdback_rate``\ ).

        When no holdback rate is defined for the item, returns ``0.0``.
        
        :returns: The holdback amount of the item. ``0.0`` if no holdback rate
                  is defined for the item.
        :rtype: :class:`float`
        """
        if self.holdback_rate is None:
            return 0.0
        else:
            return round(self.get_price() *
                         (round(self.holdback_rate, ACCURACY) / 100.), ACCURACY)

    def get_holdback_vat_amount(self):
        """    
        Computes the holdback amount on the VAT amount for this item
        (\ ``vat_amount`` * ``holdback_rate``\ ).

        When no holdback rate is defined for the item, returns ``0.0``. When no
        VAT rate is defined for the item, returns ``0.0``.
        
        :returns: The holdback amount on the VAT amount of the item. ``0.0``
                  if no holdback rate or no VAT rate is defined for the item.
        :rtype: :class:`float`
        """
        if self.vat_rate is None:
            return 0.0
        elif self.holdback_rate is None:
            return 0.0
        elif self.holdback_on_vat is False:
            return 0.0
        else:
            return round(self.get_vat_amount() *
                         (round(self.holdback_rate, ACCURACY) / 100.), ACCURACY)


class PreviousAccountingDoc:
    """
    Entity class representing an accounting document that was previously sent
    and that is used in the current bill.

    This accounting document can be a downpayment that has previously been
    charged (``Downpayment`` previously sent) or a debit that has previously
    been issued (``Debit`` previously sent). The amount of this previous
    accounting document will modify the total to be paid of the current bill.

    The real type represented by a previous accounting document depends on the
    attribute where the object will be added in the current bill
    (``charged_downpayment`` or ``issued_debit``).

    .. attribute:: total

       Attribute containing the total of the previous accounting document.

       type: :class:`float`

    .. attribute:: vat_amount

       Attribute containing the VAT amount of the previous accounting
       document. This VAT amount is a part of the ``total`` previously defined.

       type: :class:`float`

    .. attribute:: accdoc_id

       Attribute defining the identifier of the previous accounting
       document. This identifier is not the document reference but the legal
       identifier of the document (cf.  ``id``)

       type: :class:`unicode`

    .. attribute:: accdoc_date

       Attribute defining the date when the previous accounting document was
       published.

       type: :class:`unicode`

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes an empty object.
        """        
        self.total = 0.0
        self.vat_amount = 0.0
        self.accdoc_id = u""
        self.accdoc_date = u""

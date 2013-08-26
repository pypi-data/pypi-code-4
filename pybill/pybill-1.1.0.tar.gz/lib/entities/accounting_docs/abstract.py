# -*- coding: utf-8 -*-
"""
``pybill.lib.entities.accounting_docs.abstract`` module is a private
module containing the abstract class that all the high-level entity classes
inherit from.

.. autoclass:: GenericAccountingDoc
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY, PBD_1_0


class GenericAccountingDoc:
    """
    Abstract class containing common parts for ``Bill``, ``Downpayment``,
    ``ClaimForm``, ``ProForma`` and ``Debit``.

    .. attribute:: id

       Attribute defiing the iIdentifier of the accounting document. This
       attribute is legally mandatory on some documents (e.g. bills that must
       have a unique identifier). On some other documents (e.g. pro-forma, it
       doesn't make sense). Thus, can be empty for some documents.

       type: :class:`unicode`

    .. attribute:: origin_format

       Attribute containing the name of the format from which this entity was
       created.  This attribute is set by the XML reader when the entity is
       created from a file. Can be ``u"PBD-1.0"`` or ``u"PBD-0.X"``. By
       default, it is set to the latest format (i.e. ``"PBD-1.0"``).
                         
       type: :class:`unicode`

    .. attribute:: doc_ref

       Attribute defining the reference of the document. It is different from
       the identifier because the document reference is actually used for
       classifying documents in the organisation whereas the identifier is for
       legal reference. Can be empty.

       type: :class:`unicode`

    .. attribute:: date

       Attribute defining the date when the document was published; this is a
       **string representation** of the date. The ``date_num`` attribute
       contains a `date` object. There is no correlation between these two
       attributes but they often refer to the same date. Can be empty.

       type: :class:`unicode`

    .. attribute:: date_num

       Attribute defining the date when the document was published; This is a
       :class:`~datetime.date` object. The ``date`` attribute contains a string
       representation of the date. There is no correlation between these two
       attributes but they often refer to the same date. Can be None.

       type: :class:`datetime.date`

    .. attribute:: place

       Attribute defining the place where the document was written. Can be
       empty.

       type: :class:`unicode`

    .. attribute:: other_infos

       Attribute defining a dictionary whose keys are the keywords of additional
       pieces of metadata and whose values are the values associated to these
       keywords for the document. For example: u"Supplier" and the supplier
       reference.

       type: dictionary of :class:`unicode` indexed by :class:`unicode` keys

    .. attribute:: sender

       Attribute containing the identification and various information about the
       sender of the document. These pieces of information complement the
       address of the organisation that emits the document (that is read from
       the configuration file). They actually consist in the sender name, its
       job titles, its phone and email.

       type: :class:`~pybill.lib.entities.addresses.PersonAddress`

    .. attribute:: receiver

       Attribute containing the name and address of the receiver of the
       document. The name of the person is used to display the person who should
       process the document. The organisation associated to this person is used
       to know which organisation will receive (and pay) the accounting document
       (e.g. bill).

       type: :class:`~pybill.lib.entities.addresses.PersonAddress`

    .. attribute:: acc_items

       Attribute containing the list of the items that appear on the accounting
       document (e.g. items sold that appear on a bill).
                     
       type: list of :class:`~pybill.lib.entities.accounting_docs.utils.AccItem`

    .. attribute:: remarks

       Attribute containing the optional remarks. Each remark is a text
       paragraph that is displayed at the beginning of the accounting document.

       type: list of :class:`unicode`

    .. attribute:: cfg_data

       Attribute containing the configuration data that must be used to render
       the accounting document. This configuration object is attached to the
       acccounting document by the XML reader.

       type: :class:`~pybill.lib.config.entities.ConfigData`

    .. attribute:: account_numbers

       Attribute containing the numbers of the accounting accounts that should
       be impacted by this accounting document. The numbers are stored in a
       dictionary whose keys are the ``CLIENT``, ``HOLDBACK_CLIENT``,
       ``PRODUCT`` and ``VAT`` constants.

       type: dictionary of :class:`unicode` indexed by :class:`unicode` keys

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes common parts of the object.

        This method raises a ``NotImplementedError`` exception if you try to
        instantiate an object of this class (that is abstract)
        """
        if self.__class__ is GenericAccountingDoc:
            raise NotImplementedError("Abstract classes can't be instanciated")
        # document standard metadata
        self.id = u""
        self.origin_format = PBD_1_0
        self.doc_ref = u""
        self.date = u""
        self.date_num = None
        self.place = u""
        # document other metadata
        self.other_infos = {}
        # sender and receiver
        self.sender = None
        self.receiver = None
        # List of items
        self.acc_items = []
        # Other text
        self.remarks = []
        # Config object attached to the document
        self.cfg_data = None
        # Accounting information
        self.account_numbers = {}

    def has_vat_rates(self):
        """
        This methods tests if the accounting document contains items with a
        VAT rate.
        
        :returns: True if the accounting document contains at least one item
                  with a VAT rate.
        :rtype: :class:`bool`
        """
        return reduce(lambda x, y: x or y,
                      [(it.vat_rate is not None) for it in self.acc_items],
                      False)

    def has_holdbacks(self):
        """
        This methods tests if the accounting document contains items with a
        holdback rate.
        
        :returns: True if the accounting document contains at least one item
                  with a holdback rate.
        :rtype: :class:`bool`
        """
        return reduce(lambda x, y: x or y,
                     [(it.holdback_rate is not None) for it in self.acc_items],
                      False)

    def has_vat_holdbacks(self):
        """
        This methods tests if the accounting document contains items with a
        holdback rate applied on VAT.
        
        :returns: True if the accounting document contains at least one item
                  with a holdback rate that is applied on VAT amount and this
                  item has a VAT rate.
        :rtype: :class:`bool`
        """
        return reduce(lambda x, y: x or y,
                      [(it.holdback_rate is not None
                        and it.holdback_on_vat
                        and it.vat_rate is not None) for it in self.acc_items],
                      False)

    def get_all_vat_rates(self):
        """
        Returns a set of the different VAT rates applied to the accounting
        items.

        Of course, each VAT rate appears only one time in the set. The set can
        be empty if no VAT is applied to the items.
        
        :returns: Set containing the different VAT rates that are applied to the
                  accounting items of the document
        :rtype: set of :class:`float`
        """
        vat_rates = set()
        for item in [i for i in self.acc_items if i.vat_rate is not None]:
            vat_rates.add(item.vat_rate)
        return vat_rates

    def get_vat_amount_for_rate(self, vat_rate):
        """
        Computes the sum of the VAT amounts of all the accounting items that use
        the given VAT rate.

        Returns ``0.0`` if no item matches the given VAT rate.
        
        :parameter vat_rate: VAT rate. Only the items that use this VAT rate
                             will be used to compute the VAT amount.
        :type vat_rate: :class:`float`
        
        :returns: VAT amount of all the items that use the specified VAT rate.
        :rtype: :class:`float`
        """
        vat_amount = 0.0
        for item in self.acc_items:
            if item.vat_rate == vat_rate:
                vat_amount += item.get_vat_amount()
        return round(vat_amount, ACCURACY)

    def get_price_total(self):
        """
        Computes the sum of the prices (actually tax free price) for all the
        items in the accounting document.
        
        :returns: Sum of the price of all the items.
        :rtype: :class:`float`
        """
        price_total = 0.0
        for item in self.acc_items:
            price_total += item.get_price()
        return round(price_total, ACCURACY)

    def get_holdback_amount(self):
        """
        Computes the sum of the holdbacks of all the accounting items.

        Returns ``0.0`` if no item has a holdback. Please note that these
        holdbacks are on tax free prices, see method ``get_holdback_vat_amount``
        method for holdbacks on VAT amount.
        
        :returns: Sum of the holdbacks for all the items in the accounting
                  document.
        :rtype: :class:`float`
        """
        holdback_amount = 0.0
        for item in self.acc_items:
            holdback_amount += item.get_holdback_amount()
        return round(holdback_amount, ACCURACY)

    def get_holdback_vat_amount(self):
        """
        Computes the sum of the holdbacks on VAT for all the accounting items.
        
        Returns ``0.0`` if no item has a holdback or no item has a VAT rate.
        Please note that these holdbacks are on VAT amounts, see method
        ``get_holdback_amount`` method for holdbacks on tax free prices.
        
        :returns: Sum of the holdbacks on VAT amounts for all the items in the
                  accounting document.
        :rtype: :class:`float`
        """
        holdback_vat_amount = 0.0
        for item in self.acc_items:
            holdback_vat_amount += item.get_holdback_vat_amount()
        return round(holdback_vat_amount, ACCURACY)

    def get_including_taxes_total(self):
        """
        Computes the sum of the including taxes prices for all the items in the
        accounting document.

        If the document contains only items with no VAT rate defined, this total
        is identical to the total returned by ``get_price_total`` method.
        
        :returns: Sum of the including taxes prices of all the items.
        :rtype: :class:`float`
        """
        including_taxes_total = 0.0
        for item in self.acc_items:
            including_taxes_total += item.get_including_taxes_price()
        return round(including_taxes_total, ACCURACY)

    def get_to_be_paid_holdback_free(self):
        """
        Computes the total without holdbacks that must be paid.

        This abstract method will be defined in the child classes.

        :returns: The total without holdbacks that must be paid. The
                  computation of this total depends on the accounting document
                  type.
        :rtype: :class:`float`
        """
        raise NotImplementedError()

    def get_to_be_paid_holdback(self):
        """
        Computes the total of holdbacks that must be paid.

        This abstract method will be defined in the child classes.

        :returns: The total of holdbacks that must be paid. The computation of
                  this total depends on the accounting document type.
        :rtype: :class:`float`
        """
        raise NotImplementedError()

    def get_to_be_paid_vat(self):
        """
        Computes the total of VAT amounts that must be paid.

        This abstract method will be defined in the child classes.

        :returns: The total of VAT amounts that must be paid. The computation 
                  of this total depends on the accounting document type.
        :rtype: :class:`float`
        """
        raise NotImplementedError()

    def get_to_be_paid(self):
        """
        Computes the total that must be paid.

        This method can be redefined in the child classes.

        Actually it is::

            total without holdbacks to be paid + total of holdbacks to be paid

        :returns: The total that must be paid. The computation of this total
                  depends on the accounting document type.
        :rtype: :class:`float`
        """
        return round(self.get_to_be_paid_holdback_free()
                     + self.get_to_be_paid_holdback(), ACCURACY)

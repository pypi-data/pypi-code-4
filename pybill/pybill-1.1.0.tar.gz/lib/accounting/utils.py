# -*- coding: utf-8 -*-
"""
``pybill.lib.accounting.utils`` module contains some useful constants and the
basic classes used in the accounting entries generation.

The constants are used to designate the various account numbers used in the
accounting entries generation. These account numbers are stored in a dictionary
defined in each PyBill accounting entity.

.. autodata:: CLIENT

.. autodata:: CLIENT_HOLDBACK

.. autodata:: PRODUCT

.. autodata:: VAT

The basic class describes an accounting entry.

.. autoclass:: Entry
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY
from pybill.lib.errors import PyBillProcessingException


CLIENT = u"Client"
"""
Constant used to designate, in the dictionaries, the account number of the
Client account used for an accounting document.

type: :class:`unicode`
"""

CLIENT_HOLDBACK = u"Client Holdback"
"""
Constant used to designate, in the dictionaries, the account number of the
Client Holdback account used for an accounting document.

type: :class:`unicode`
"""

PRODUCT = u"Product"
"""
Constant used to designate, in the dictionaries, the account number of the
Product account used for an accounting document.

type: :class:`unicode`
"""

VAT = u"VAT"
"""
Constant used to designate, in the dictionaries, the account number of the VAT
account used for an accounting document.

type: :class:`unicode`
"""


class Entry:
    """
    Little class representing an accounting entry.

    This entry is quite basic and contains only a date, an explanation, a list
    of debits and a list of credits.

    .. attribute:: date

       Attribute containing the date of the entry.

       type: :class:`datetime.date`

    .. attribute:: explanation

       Attribute containing the explanation of the entry.

       type: :class:`unicode`

    .. attribute:: credits

       Attribute containing a dictionary of account numbers (dictionary keys)
       associated with the amounts (floats) that must be credited on these
       accounts.

       type: dictionary of :class:`float` indexed by :class:`unicode` keys

    .. attribute:: debits

       Attribute containing a dictionary of account numbers (dictionary keys)
       associated with the amounts (floats) that must be debited on these
       accounts.

       type: dictionary of :class:`float` indexed by :class:`unicode` keys

    .. automethod:: __init__
    """
    def __init__(self, date, explanation):
        """
        Initializes a new accounting entry.

        :parameter date: Date of the entry.
        :type date: :class:`datetime.date`

        :parameter explanation: Explanation of the entry
        :type explanation: :class:`unicode`
        """
        self.date = date
        self.explanation = explanation
        self.credits = {}
        self.debits = {}

    def add_movement(self, account_number, amount):
        """
        Adds a movement of ``amount`` on the account whose number is
        ``account_number``.

        If the amount is positive, the account will be credited, else the
        account will be debited.

        :parameter account_number: Number of the accounting account that will
                                   be credited or debited in this entry.
        :type account_number: :class:`unicode`

        :parameter amount: Amount of the movement on the account
                           ``account_number``. If the amount is positive, the
                           account is credited, else it is debited.
        :type amount: :class:`float`
        """
        if amount >= 0:
            amts_list = self.credits.setdefault(account_number, [])
            amts_list.append(round(amount, ACCURACY))
        else:
            amts_list = self.debits.setdefault(account_number, [])
            amts_list.append(round(-amount, ACCURACY))

    def check(self):
        """
        Checks the accounting entry.

        That's to say, checks if the sum of the debits is equal to the sum
        of the credits. Raises an exception if it's not the case.
        """
        debit_amounts = 0.0
        for account, amounts in self.debits.items():
            debit_amounts += sum(amounts)
        credit_amounts = 0.0
        for account, amounts in self.credits.items():
            credit_amounts += sum(amounts)
        if abs(debit_amounts -credit_amounts) > 10**-(ACCURACY+3):
            raise PyBillProcessingException("Generated accounting entry %s "
                                            "has a different sum for its "
                                            "debits and its credits." % self)
        else:
            return True

    def __repr__(self):
        """
        :returns: A string representation of the accounting entry.
        :rtype: :class:`str`
        """
        str_repr = "<Entry "
        for account, amounts in self.credits.items():
            for amount in amounts:
                str_repr += "(Cred %s: %s) " % (account, amount)
        for account, amounts in self.debits.items():
            for amount in amounts:
                str_repr += "(Deb %s: %s) " % (account, amount)
        str_repr += ">"
        return str_repr

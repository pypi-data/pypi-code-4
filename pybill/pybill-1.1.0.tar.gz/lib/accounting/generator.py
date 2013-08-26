# -*- coding: utf-8 -*-
"""
``pybill.lib.accounting.generator`` module defines the class that can generate
accounting entries from the accounting documents (PyBill entities).

This class can be used to generate the accounting entries for several documents
and then to save the entries into an XML file.

.. autoclass:: EntriesGenerator
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

import datetime
from lxml import etree

from pybill.lib import ACCURACY
from pybill.lib.xmlwriters.utils import ENCODING, open_xml_outfile
from pybill.lib.accounting.utils import CLIENT, CLIENT_HOLDBACK, PRODUCT, VAT
from pybill.lib.entities.accounting_docs import (Bill, ClaimForm, Debit,
                                                 Downpayment, ProForma)
from pybill.lib.accounting.utils import Entry


# Dictionary associating accounting document classes with keywords.
TYPENAME = {Bill: u"bill", ClaimForm: u"claim-form", Debit: u"debit",
            Downpayment: u"downpayment", ProForma: u"pro-forma"}

# Default account numbers used when no account number is specified in the
# accounting documents.
DEFAULT_PRODUCT = u"70"
DEFAULT_CLIENT = u"411"
DEFAULT_VAT = u"445"


class EntriesGenerator:
    """
    Class that generates accounting entries from the accounting documents
    (PyBill entities).

    This class generates a unique list of accounting entries from a set of
    accounting documents, each document generating a single entry. This list
    can be written to an XML file with the dedicated method.

    The accounting entries are generated in `pycompta` format.

    .. attribute:: entries

        Attribute containing a list of accounting entries generated from the
        accounting documents. When generating the entry for a new accounting
        document, it will be appended to this list.

        This list is usually emptied after the entries have been written into an
        XML document.

        type: list of :class:`~pybill.lib.accounting.utils.Entry`

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Initializes the generator.
        """
        self.entries = None
        self.reset_entries()

    def reset_entries(self):
        """
        Erases all the previously generated entries and starts with a new
        empty list of entries.
        """
        self.entries = []

    def generate_entry(self, acc_doc):
        """
        Generates the accounting entry from the ``acc_doc`` document and adds
        it to the list in this class.

        :parameter acc_doc: Accounting document from which the accounting entry
                            will be generated.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`
        """
        if acc_doc.__class__ in [ProForma]:
            # Nothing to do as ``acc_doc`` is only a hypothetic future bill.
            pass
        else:
            # Builds a new accounting entry with the date & explanation fields.
            if acc_doc.date_num is not None:
                acc_date = acc_doc.date_num
            else:
                acc_date = datetime.date.today()
            expl = (u"%s %s %s" % (
                acc_doc.cfg_data.get_local_phrase(TYPENAME[acc_doc.__class__]),
                acc_doc.cfg_data.get_local_phrase(u"number"),
                acc_doc.id))
            entry = Entry(acc_date, expl)
            # Fills the accounting entry with credits and debits.
            prod_account = acc_doc.account_numbers.get(PRODUCT, DEFAULT_PRODUCT)
            vat_account = acc_doc.account_numbers.get(VAT, DEFAULT_VAT)
            cli_account = acc_doc.account_numbers.get(CLIENT, DEFAULT_CLIENT)
            hlb_account = acc_doc.account_numbers.get(CLIENT_HOLDBACK,
                                                      cli_account)
            no_hlb = acc_doc.get_to_be_paid_holdback_free()
            hlb = acc_doc.get_to_be_paid_holdback()
            vat = acc_doc.get_to_be_paid_vat()
            if acc_doc.__class__ in [Bill, ClaimForm, Downpayment]:    
                entry.add_movement(prod_account, (no_hlb + hlb - vat))
                if abs(vat) > 10**-(ACCURACY + 3):
                    entry.add_movement(vat_account, vat)
                entry.add_movement(cli_account, -no_hlb)
                if abs(hlb) > 10**-(ACCURACY + 3):
                    entry.add_movement(hlb_account, -hlb)
            elif acc_doc.__class__ in [Debit]:
                entry.add_movement(prod_account, -(no_hlb + hlb - vat))
                if abs(vat) > 10**-(ACCURACY + 3):
                    entry.add_movement(vat_account, -vat)
                entry.add_movement(cli_account, no_hlb)
                if abs(hlb) > 10**-(ACCURACY + 3):
                    entry.add_movement(hlb_account, hlb)
            else:
                raise Exception("Unknown class of accounting document for %s:"
                                " %s" % (acc_doc.id, acc_doc.__class__))
            # Checks the accounting entry and adds it to the list.
            entry.check()
            self.entries.append(entry)

    def write_entries_in_xml(self, xml_file, encoding=ENCODING):
        """
        Exports the generated accounting entries in an XML file.

        :parameter xml_file: Name of the file where the accounting entries
                             will be exported to.
        :type filename: :class:`unicode`

        :parameter encoding: Encoding used to write the XML file.
        :type encoding: :class:`str`
        """
        # Builds the XML document containing the accounting entries.
        root_xml = etree.Element(u"ecritures")
        for entry in self.entries:
            entry_xml = etree.SubElement(root_xml, u"ecriture")
            entry_xml.set(u"date", unicode(entry.date.strftime("%Y-%m-%d")))
            explan_xml = etree.SubElement(entry_xml, u"libelle")
            explan_xml.text = unicode(entry.explanation)
            for account in sorted(entry.debits):
                for amount in entry.debits[account]:
                    dbt_xml = etree.SubElement(entry_xml, u"debit")
                    dbt_xml.set(u"compte", unicode(account))
                    dbt_xml.set(u"montant", unicode(amount))
            for account in sorted(entry.credits):
                for amount in entry.credits[account]:
                    dbt_xml = etree.SubElement(entry_xml, u"credit")
                    dbt_xml.set(u"compte", unicode(account))
                    dbt_xml.set(u"montant", unicode(amount))
        # Opens the XML file and writes the XML document in it.
        if len(self.entries) > 0:
            out = open_xml_outfile(xml_file, encoding=encoding)
            out.write(etree.tostring(root_xml, encoding=encoding,
                                     pretty_print=True, xml_declaration=False))

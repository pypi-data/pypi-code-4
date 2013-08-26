# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.flowgenerators.bill_generator`` module defines the flow
generator for the bill entities.

The flow generator generates the title, various paragraphes, the main table
detailling the items, and the total table. This flow content will be displayed
on various pages by the
:class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
document template with the platypus machinery.

.. autoclass:: BillFlowGenerator
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib.pdfwriters.flowgenerators.abstract import AbstractFlowGenerator
from pybill.lib.pdfwriters.utils import escape_text


class BillFlowGenerator(AbstractFlowGenerator):
    """
    Class generating the PDF flow content for a
    :class:`~pybill.lib.entities.accounting_docs.bill.Bill`.

    .. automethod:: _get_acc_doc_title

    .. automethod:: _get_total_table_cell_contents
    """
    def _get_acc_doc_title(self, acc_doc):
        """
        Gives the title of the accounting document (here, a bill).

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: The accounting document title.
        :rtype: :class:`unicode`
        """
        return (u"<b>%s %s %s</b> %s %s" 
                % (escape_text(acc_doc.cfg_data.get_local_phrase(u'bill')),
                   escape_text(acc_doc.cfg_data.get_local_phrase(u'number')),
                   escape_text(acc_doc.id, True),
                   escape_text(acc_doc.cfg_data.get_local_phrase(u'dated')),
                   escape_text(acc_doc.date, True)))

    def _get_total_table_cell_contents(self, acc_doc):
        """
        Gives the contents of the cells of the total table.

        These contents will be used by the ``_get_total_table`` method to build
        the total table.

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF (here a bill).
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns:
            A list describing the cells of the total table. The first element is
            a list of unicode strings corresponding to the various lines of the
            name of the row; the second element is a float corresponding to the
            number written in the row; the third element is a specification of
            the style of the row (``u"bold"``, ``u"italic"``,
            ``u"bold italic"``, ``u""``). 
        :rtype: list of triples (list of :class:`unicode`, :class:`float`,
                :class:`unicode`)
        """
        cfg_data = acc_doc.cfg_data
        contents = []
        contents.extend(
            self._build_cell_contents_for_totals(acc_doc))
        # Optional next rows (downpayments already charged).
        for dwp in acc_doc.charged_downpayments :
            name = [cfg_data.get_local_phrase(u'charged-downpayment')]
            if dwp.accdoc_id.strip() != u"":
                name.append(u"%s %s" % (cfg_data.get_local_phrase(u'number'),
                                        dwp.accdoc_id))
            if dwp.accdoc_date.strip() != u"":
                name.append(u"%s %s" \
                                 % (cfg_data.get_local_phrase(u'charged-on'),
                                    dwp.accdoc_date))
            number = dwp.total * -1
            contents.append((name, number, u"regular"))
        # Optional next rows (previously issued debits).
        for dbt in acc_doc.issued_debits :
            name = [cfg_data.get_local_phrase(u'issued-debit')]
            if dbt.accdoc_id.strip() != u"":
                name.append(u"%s %s" % (cfg_data.get_local_phrase(u'number'),
                                        dbt.accdoc_id))
            if dbt.accdoc_date.strip() != u"":
                name.append(u"%s %s" \
                                    % (cfg_data.get_local_phrase(u'issued-on'),
                                       dbt.accdoc_date))
            number = dbt.total * -1
            contents.append((name, number, u"regular"))
        # Next row (amount to be paid).
        name = [cfg_data.get_local_phrase(u'to-be-paid')]
        number = acc_doc.get_to_be_paid_holdback_free()
        contents.append((name, number, u"bold"))
        # Next row (holdbacks to be paid).
        if acc_doc.has_holdbacks():
            name = [cfg_data.get_local_phrase(u'to-be-paid'), 
                    cfg_data.get_local_phrase(u'holdback'), ]
            number = acc_doc.get_to_be_paid_holdback()
            contents.append((name, number, u"bold"))
        return contents

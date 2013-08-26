# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.flowgenerators.bill_generator`` module defines the flow
generator for the claim form entities.

The flow generator generates the title, various paragraphes, the main table
detailling the items, and the total table. This flow content will be displayed
on various pages by the
:class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
document template with the platypus machinery.

.. autoclass:: ClaimFormFlowGenerator
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib.pdfwriters.flowgenerators.abstract import AbstractFlowGenerator
from pybill.lib.pdfwriters.utils import escape_text


class ClaimFormFlowGenerator(AbstractFlowGenerator):
    """
    Class generating the PDF flow content for a
    :class:`~pybill.lib.entities.accounting_docs.claimform.ClaimForm`.

    .. automethod:: _get_acc_doc_title

    .. automethod:: _get_total_table_cell_contents
    """
    def _get_acc_doc_title(self, acc_doc):
        """
        Gives the title of the accounting document (here, a claim form).

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: The accounting document title.
        :rtype: :class:`unicode`
        """
        return (u"<b>%s %s %s</b> %s %s" 
              % (escape_text(acc_doc.cfg_data.get_local_phrase(u'claim-form')),
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
                            exported in PDF (here a claim form).
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
        contents = []
        contents.extend(
            self._build_cell_contents_for_totals(acc_doc))
        # Next row (amount to be paid).
        name = [acc_doc.cfg_data.get_local_phrase(u'to-be-paid')]
        number = acc_doc.get_to_be_paid_holdback_free()
        contents.append((name, number, u"bold"))
        # Next row (holdbacks to be paid).
        if acc_doc.has_holdbacks():
            name = [acc_doc.cfg_data.get_local_phrase(u'to-be-paid'), 
                    acc_doc.cfg_data.get_local_phrase(u'holdback'), ]
            number = acc_doc.get_to_be_paid_holdback()
            contents.append((name, number, u"bold"))
        return contents

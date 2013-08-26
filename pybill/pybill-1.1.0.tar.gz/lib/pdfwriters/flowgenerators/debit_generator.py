# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.flowgenerators.debit_generator`` module defines the flow
generator for the debit entities.

The flow generator generates the title, various paragraphes, the main table
detailling the items, and the total table. This flow content will be displayed
on various pages by the
:class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
document template with the platypus machinery.

.. autoclass:: DebitFlowGenerator
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib.pdfwriters.flowgenerators.abstract import AbstractFlowGenerator

from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Table, TableStyle

from pybill.lib.pdfwriters import style_normal_left
from pybill.lib.pdfwriters.utils import escape_text


class DebitFlowGenerator(AbstractFlowGenerator):
    """
    Class generating the PDF flow content for a
    :class:`~pybill.lib.entities.accounting_docs.debit.Debit`.

    .. automethod:: _get_acc_doc_title

    .. automethod:: _get_bottom_left_element

    .. automethod:: _get_total_table_cell_contents
    """
    def _get_acc_doc_title(self, acc_doc):
        """
        Gives the title of the accounting document (here, a debit).

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: The accounting document title.
        :rtype: :class:`unicode`
        """
        return (u"<b>%s %s %s</b> %s %s"
                % (escape_text(acc_doc.cfg_data.get_local_phrase(u'debit')),
                   escape_text(acc_doc.cfg_data.get_local_phrase(u'number')),
                   escape_text(acc_doc.id, True),
                   escape_text(acc_doc.cfg_data.get_local_phrase(u'dated')),
                   escape_text(acc_doc.date, True)))

    def _get_bottom_left_element(self, acc_doc):
        """
        Gives the element that must be displayed at the bottom left of
        the accounting document.

        In the case of a debit, this element is nothing.
        
        :parameter acc_doc: The current accounting document that must be
                            exported in PDF (here, a debit).
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: An empty table to be displayed in the bottom left of the PDF
                  document.
        :rtype: :class:`reportab.platypus.Flowable`
        """
        # Builds an empty table (with its style).
        empty_table = Table([[Paragraph(u"", style_normal_left)]],
                            [9*cm], None)
        empty_table.setStyle(
            TableStyle([ ('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                         ('VALIGN',    (0,0), (-1,-1), 'TOP'),
                       ])
                           )
        return empty_table

    def _get_total_table_cell_contents(self, acc_doc):
        """
        Gives the contents of the cells of the total table.

        These contents will be used by the ``_get_total_table`` method to build
        the total table.

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF (here a debit).
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
        # Last row (debit total).
        name = [acc_doc.cfg_data.get_local_phrase(u'debit-total')]
        number = acc_doc.get_to_be_paid()
        contents.append((name, number, u"bold"))
        return contents

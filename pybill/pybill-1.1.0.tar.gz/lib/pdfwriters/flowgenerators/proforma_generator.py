# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.flowgenerators.proforma_generator`` module defines the
flow generator for the pro-forma entities.

The flow generator generates the title, various paragraphes, the main table
detailling the items, and the total table. This flow content will be displayed
on various pages by the
:class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
document template with the platypus machinery.

.. autoclass:: ProFormaFlowGenerator
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib.pdfwriters.flowgenerators.abstract import AbstractFlowGenerator

from reportlab.lib.units import cm

from reportlab.platypus import Paragraph, Table, TableStyle

from pybill.lib.pdfwriters import style_little_center
from pybill.lib.pdfwriters.utils import escape_text


class ProFormaFlowGenerator(AbstractFlowGenerator):
    """
    Class generating the PDF flow content for a
    :class:`~pybill.lib.entities.accounting_docs.proforma.ProForma`.

    .. automethod:: _get_acc_doc_title

    .. automethod:: _get_bottom_left_element

    .. automethod:: _get_total_table_cell_contents
    """
    def _get_acc_doc_title(self, acc_doc):
        """
        Gives the title of the accounting document (here, a pro-forma).

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: The accounting document title.
        :rtype: :class:`unicode`
        """
        return (u"<b>%s</b> %s %s"
             % (escape_text(acc_doc.cfg_data.get_local_phrase(u'pro-forma')),
                escape_text(acc_doc.cfg_data.get_local_phrase(u'valid-until')),
                escape_text(acc_doc.validity_date, True)))
    
    def _get_bottom_left_element(self, acc_doc):
        """
        Gives the element that must be displayed at the bottom left of
        the accounting document.

        In the case of a pro-forma, this element is a set of lines asking for
        the agreement of the receiver.
        
        :parameter acc_doc: The current accounting document that must be
                            exported in PDF (here, a pro-forma).
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: A table with a single cell containing the agreement lines
                  read from the configuration. This table is to be displayed
                  in the bottom left of the PDF document.
        :rtype: :class:`reportlab.platypus.Flowable`
        """
        table_data = [[]]
        # First and single row contains a single cell with several paragraphs.
        cell = []
        for line in acc_doc.cfg_data.agreement_intro_lines:
            cell.append(Paragraph(escape_text(line), style_little_center))
        table_data[0].append(cell)
        # Builds the agreement table (with its style).
        agr_table = Table(table_data, [9*cm], None)
        agr_table.setStyle(
            TableStyle([ ('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                         ('VALIGN',    (0,0), (-1,-1), 'TOP'),
                       ])
                           )
        return agr_table

    def _get_total_table_cell_contents(self, acc_doc):
        """
        Gives the contents of the cells of the total table.

        These contents will be used by the ``_get_total_table`` method to build
        the total table.

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF (here a pro-forma).
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
        return contents

# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.flowgenerators.abstract`` module defines the abstract
base class used by all the PyBill-specific flow generators.

.. autoclass:: AbstractFlowGenerator
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib import ACCURACY
from reportlab.lib.units import cm
from reportlab.lib.colors import black

from reportlab.platypus import Paragraph, Spacer, KeepTogether
from reportlab.platypus import Table, TableStyle

from pybill.lib.pdfwriters import (style_title, style_normal_left,
                                   style_normal_center, style_normal_right,
                                   style_normal_just, style_little_indent_left,
                                   style_little_center, style_little_left)

from pybill.lib.pdfwriters.utils import TotalizableTable, NumberParagraph
from pybill.lib.pdfwriters.utils import escape_text, format_number


class AbstractFlowGenerator:
    """
    Abstract class containing the common parts for generating the PDF flow
    content for the various kinds of accounting documents (bill, claim form,
    downpayment, debit, pro-forma). Specific parts
    are generated in the  derived classes (one for each kind of document)
    (cf. `Template` design pattern).

    For a correct behaviour, you must use a flow generator corresponding to
    the kind of accounting document you want to render in PDF.
    
    The PDF flow content is a list of :class:`reportlab.platypus.Flowable`
    objects that will be displayed on various pages by the document
    template and the platypus machinery.

    .. automethod:: __init__

    .. automethod:: generate_flow

    .. automethod:: _get_acc_doc_title

    .. automethod:: _get_items_table
    
    .. automethod:: _get_bottom_left_element

    .. automethod:: _get_total_table

    .. automethod:: _get_total_table_cell_contents

    .. automethod:: _build_cell_contents_for_totals

    """
    def __init__(self):
        """
        Initializes the flow generator.

        This constructor should never be called directly as this class is
        abstract.
        """
        if self.__class__ is AbstractFlowGenerator:
            raise NotImplementedError("Abstract class can't be instanciated")

    def generate_flow(self, acc_doc):
        """
        Generates the flow content (a list of
        :class:`~reportlab.platypus.Flowable`) for the accounting
        document.
        
        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: A list of flowable objects to be displayed by the PDF
                  document template.
        :rtype: list of :class:`reportlab.platypus.Flowable`
        """
        flow_list = []
        # Title.
        flow_list.append(Paragraph(self._get_acc_doc_title(acc_doc),
                                   style_title))
        # Introduction text.
        txt = acc_doc.cfg_data.get_local_phrase(u'intro-detail')
        if txt != u"":
            flow_list.append(Spacer(1, 0.1*cm))
            flow_list.append(Paragraph(u"<i>%s</i>" % escape_text(txt),
                                       style_little_left))
        # Optional remarks.
        for rem in [r.strip() for r in acc_doc.remarks if r.strip() != u""]:
            flow_list.append(Spacer(1, 0.2*cm))
            flow_list.append(Paragraph(escape_text(rem, True),
                                       style_normal_just))
        # End of the top part of the document.
        flow_list.append(Spacer(1, 0.5*cm))
        # Items table (main table).
        flow_list.append(self._get_items_table(acc_doc))
        # End of the body part of the document.
        flow_list.append(Spacer(1, 0.5*cm))
        # Bottom table containing en element on the left (table of payment
        # terms or set of paragraphs for the pro-forma) and the total table
        # on the right.
        bott_table = Table([[self._get_bottom_left_element(acc_doc),
                             u" ",
                             self._get_total_table(acc_doc)]],
                           [9*cm, 2.5*cm, 7.5*cm], None)
        bott_table.setStyle(
            TableStyle([ ('ALIGN',         (0,0), ( 0,-1), 'LEFT'),
                         ('ALIGN',         (2,0), ( 2,-1), 'RIGHT'),
                         ('VALIGN',        (0,0), (-1,-1), 'TOP'),
                         ('LEFTPADDING',   (0,0), (-1,-1), 0),
                         ('RIGHTPADDING',  (0,0), (-1,-1), 0),
                         ('TOPPADDING',    (0,0), (-1,-1), 0),
                         ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                       ])
            )
        # The table is in a ``KeepTogether`` because we don't want it to be
        # splitted on two pages.
        flow_list.append(KeepTogether([bott_table]))
        return flow_list

    def _get_acc_doc_title(self, acc_doc):
        """
        Gives the title of the accounting document.

        The title depends on the kind of document. This abstract method will be
        defined in the children classes.

        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: The accounting document title.
        :rtype: :class:`unicode`
        """
        raise NotImplementedError()

    def _get_items_table(self, acc_doc):
        """
        Gives the main table of the accounting document that details the
        items.

        The table can be a 5 columns table (quantity, description, vat
        rate, tax free unit price, tax free price) or a 4 columns table
        (quantity, description, tax free unit price, tax free price).

        The table is a :class:`~pybill.lib.pdfwriters.utils.TotalizableTable`
        instead of a classic :class:`reportlab.platypus.Table` because we need
        this specific table to compute the carry forwards in the
        :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        document template. Inside this specific table, in each row, we insert
        one :class:`~pybill.lib.pdfwriters.utils.NumberParagraph` that contains
        the total of the row. This allows us to know what to add in the carry
        forward.
        
        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns:
            The table detailling the items. This table is a
            :class:`~pybill.lib.pdfwriters.utils.TotalizableTable` to allow the
            computation of the carry forwards in the document template. The
            items table have 4 columns when the accounting document has no VAT
            rate and 5 columns when at least one item of the accounting document
            has a VAT rate.
        :rtype: :class:`~pybill.lib.pdfwriters.utils.TotalizableTable`
        """
        cfg_data = acc_doc.cfg_data
        table_data = []
        # Header row.
        row = []
        row.append(Paragraph(
                           escape_text(cfg_data.get_local_phrase(u'quantity')),
                             style_little_center))
        row.append(Paragraph(
                        escape_text(cfg_data.get_local_phrase(u'description')),
                             style_little_center))
        if acc_doc.has_vat_rates():
            row.append(Paragraph(
                           escape_text(cfg_data.get_local_phrase(u'vat-rate')),
                                 style_little_center))
            row.append(Paragraph(
                      escape_text(cfg_data.get_local_phrase(u'tf-unit-price')),
                                 style_little_center))
            row.append(Paragraph(
                           escape_text(cfg_data.get_local_phrase(u'tf-price')),
                                 style_little_center))
        else:
            row.append(Paragraph(
                         escape_text(cfg_data.get_local_phrase(u'unit-price')),
                                 style_little_center))
            row.append(Paragraph(
                              escape_text(cfg_data.get_local_phrase(u'price')),
                                 style_little_center))            
        table_data.append(row)
        # Item rows.
        for item in acc_doc.acc_items:
            row = []
            # First cell: quantity.
            row.append(Paragraph(format_number(item.quantity,
                                               item.quantity_digits,
                                               cfg_data.number_separators),
                                 style_little_center) )
            # Second cell: description (list of paragraphs).
            cell = []
            cell.append(Paragraph(escape_text(item.title, True),
                                  style_normal_left))
            for detail in item.details:
                cell.append(Paragraph(u"<i>%s</i>" % escape_text(detail, True),
                                      style_little_indent_left))
            if item.holdback_rate is not None:
                cell.append(Spacer(0.1*cm, 1))
                text = u"%s " % cfg_data.get_local_phrase(u"holdback-on")
                if item.holdback_on_vat and item.vat_rate is not None:
                    text += cfg_data.get_local_phrase(u"it-price")
                elif item.vat_rate is not None:
                    text += cfg_data.get_local_phrase(u"tf-price")
                else:
                    text += cfg_data.get_local_phrase(u"price")
                text += u"%s %s%% %s %s" \
                        % (cfg_data.get_local_phrase(u"colon"),
                           format_number(item.holdback_rate, ACCURACY,
                                         cfg_data.number_separators),
                           cfg_data.get_local_phrase(u"ita-est"),
                           format_number(item.get_holdback_amount(), ACCURACY,
                                         cfg_data.number_separators))
                if item.holdback_on_vat and item.vat_rate is not None:
                    text += " + %s" \
                            % (format_number(item.get_holdback_vat_amount(),
                                         ACCURACY, cfg_data.number_separators))
                cell.append(Paragraph(escape_text(text), style_normal_left))
            row.append(cell)
            # Third cell: VAT rate (only if the document has VAT rates).
            if acc_doc.has_vat_rates():
                if item.vat_rate is not None:
                    text = u"%s%%" % format_number(item.vat_rate, ACCURACY,
                                                   cfg_data.number_separators)
                else:
                    text = u""
                row.append(Paragraph(text, style_normal_right))
            # Third/Fourth cell: tax free unit price.
            row.append(Paragraph(format_number(item.unit_price,
                           item.unit_price_digits, cfg_data.number_separators),
                                 style_normal_right))
            # Fourth/Fifth cell: tax free price (total of the row).
            # We don't forget to use a ``NumberParagraph`` in order to be
            # able to process the carry forward with the ``TotalizableTable``.
            row.append(NumberParagraph(item.get_price(),
                                       format_number(item.get_price(), ACCURACY,
                                                   cfg_data.number_separators),
                                       style_normal_right))
            table_data.append(row)
        if acc_doc.has_vat_rates():
            # 5 columns table.
            table_dims = [1.5*cm, 10*cm, 2*cm, 2.5*cm, 3*cm]
        else:
            # 4 columns table.
            table_dims = [1.5*cm, 12*cm, 2.5*cm, 3*cm]
        # We use a ``TotalizableTable`` in order to be able to compute the
        # carry forward with the ``AccDocDocumentTemplate`` document template.
        table = TotalizableTable(table_data, table_dims, None)
        table.repeatRows = 1 # When splitting the table, repeats first row.
        table.setStyle(
            TableStyle([ ('ALIGN',        (0,0), (-1, 0), 'CENTER'),
                         ('ALIGN',        (0,1), ( 0,-1), 'RIGHT'),
                         ('ALIGN',        (1,1), ( 1,-1), 'LEFT'),
                         ('ALIGN',        (2,1), (-1,-1), 'RIGHT'),
                         ('VALIGN',       (0,0), (-1,-1), 'TOP'),
                         ('BOX',          (0,0), (-1,-1), 0.5, black),
                         ('BOX',          (0,0), (-1, 0), 0.5, black),
                         ('INNERGRID',    (0,0), (-1,-1), 0.25,black),
                         ('LEFTPADDING',  (0,0), (-1, 0), 3),
                         ('RIGHTPADDING', (0,0), (-1, 0), 3),
                       ])
                      )
        return table

    def _get_bottom_left_element(self, acc_doc):
        """
        Gives the element that must be displayed at the bottom left of
        the accounting document.

        This element depends on the kind of document, but is actually a payment
        terms table. This method can be redefined in the children classes.
        
        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: A flowable  object contaning the content to be displayed
                  in the bottom left of the PDF document.
        :rtype: :class:`reportlab.platypus.Flowable`
        """
        table_data = []
        # First row contains a single cell with the payment terms.
        row = []
        row.append(Paragraph(
              escape_text(acc_doc.cfg_data.get_local_phrase(u'payment-terms')),
                             style_normal_center))
        table_data.append(row)
        #second row contains a single cell with several paragraphs (bank data).
        cell = [] 
        if acc_doc.payment_terms.strip() != u"":
            cell.append(Paragraph(escape_text(acc_doc.payment_terms, True),
                                  style_normal_left))
        for bk_line in acc_doc.cfg_data.bank_data_lines:
            cell.append(Paragraph(escape_text(bk_line), style_normal_left))
        table_data.append([cell])
        # Builds the payment terms table (with its style).
        pt_table = Table(table_data, [9*cm], None)
        pt_table.setStyle(
            TableStyle([ ('ALIGN',     (0,0), (-1, 0), 'CENTER'),
                         ('ALIGN',     (0,1), (-1, 1), 'LEFT'),
                         ('VALIGN',    (0,0), (-1,-1), 'TOP'),
                         ('BOX',       (0,0), (-1,-1), 0.50, black),
                         ('INNERGRID', (0,0), (-1,-1), 0.25, black),
                       ])
                         )
        return pt_table

    def _get_total_table(self, acc_doc):
        """
        Gives the total table of the accounting document (this table appears at
        the bottom right of the PDF document).

        The content of this table depends on the kind of document.
        
        This method relies on the :meth:`_get_total_table_cell_contents` that
        gives the contents of the cells of this table. This method builds
        a :class:`~reportlab.platypus.Table` object with these contents.
        
        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :returns: The total table. This table embeds its style and is ready to
                  be inserted in the flow.
        :rtype: :class:`reportlab.platypus.Table`
        """
        table_data = []
        for name, number, style in \
                        self._get_total_table_cell_contents(acc_doc):
            start_tag = end_tag = u""
            if u"bold" in style.split():
                start_tag += u"<b>"
                end_tag = u"</b>" + end_tag
            if u"italic" in style.split():
                start_tag += u"<i>"
                end_tag = u"</i>" + end_tag
            row = []
            if name is None or name == []:
                cell = [Paragraph(u"", style_normal_left)]
            else:
                cell = [Paragraph(u"%s%s%s" %(start_tag,
                                              escape_text(name[0], True),
                                              end_tag),
                                  style_normal_left)]
                cell.extend([Paragraph(u"%s%s%s" %(start_tag,
                                                   escape_text(line, True),
                                                   end_tag),
                                       style_little_left)
                             for line in name[1:]])
            row.append(cell)
            row.append(Paragraph("%s%s%s" %(start_tag,
                                            format_number(number, ACCURACY,
                                           acc_doc.cfg_data.number_separators),
                                            end_tag),
                                 style_normal_right))
            table_data.append(row)
        table = Table(table_data, [4.5*cm, 3*cm], None)
        table.setStyle(
            TableStyle([ ('ALIGN',     (0,0), ( 0,-1), 'LEFT'),
                         ('ALIGN',     (1,0), ( 1,-1), 'RIGHT'),
                         ('VALIGN',    (0,0), (-1,-1), 'MIDDLE'),
                         ('BOX',       (0,0), (-1,-1), 0.50, black),
                         ('INNERGRID', (0,0), (-1,-1), 0.25, black),
                       ])
                      )
        return table

    def _get_total_table_cell_contents(self, acc_doc):
        """
        Gives the contents of the cells of the total table.

        These contents will be used by the :meth:`_get_total_table` method to
        build the total table.  The cell contents depend on the kind of
        accounting document currently processed.
        
        The contents of the cells are given as a list of triples: name,
        number and style. Each couple corresponds to one row of the total
        table.

        - The name is a list of unicode strings corresponding to several
          lines describing the content of the row. It is written in the first
          cell of the row. The first line is written with the regular font,
          the next are written with littler font.

        - The number is a float corresponding to the amount of the row. It is
          written in the second cell of the row.

        - The style is a specification of how the row must be displayed. It can
          contain u"bold", u"italic", both or none of them.

        Please note that the name will be escaped when inserted in the table.
        Therefore it should not contain any tag of style. You should use the
        style element in the triple to specify the style of the row.

        This method is abstract and will be implemented in the child classes.
        
        :parameter acc_doc: The current accounting document that must be
                            exported in PDF.
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
        raise NotImplementedError()

    def _build_cell_contents_for_totals(self, acc_doc):
        """
        Builds the cell contents corresponding to the first rows of the total
        table.

        These rows describe the totals (tax free total, vat amounts,
        including taxes total, holdbacks). As they are inserted in the total
        tables generated by all the subclasses, they have been factorized here.

        See :meth:`_get_total_table_cell_contents` method for a description of
        the triples describing the cell contents in the total table.

        This method generates different rows if the accounting document contain
        or doesn't contain VAT rates, contain or doesn't contain holdbacks. If
        it has got VAT rates, the totals rows will be: tax free total, various
        VAT amounts, including taxes total. If it hasn't got VAT rates, the
        totals rows will be: total. If it has holdbacks, two or three more rows
        will be added: holdbacks on tax free amounts and holdbacks on VAT
        amounts (if the holdbacks are on VAT) and holdbacks to be paid.

        :returns:        
            A list describing the first cells of the total table, corresponding
            to the totals. The first element is a list of unicode strings
            corresponding to the various lines of the name of the row; the
            second element is a float corresponding to the number written in the
            row; the third element is a specification of the style of the row
            (``u"bold"``, ``u"italic"``, ``u"bold italic"``, ``u""``). 
        :rtype: list of triples (list of :class:unicode`, :class:`float`,
                :class:`unicode`)
        """
        cfg_data = acc_doc.cfg_data
        contents = []
        if not acc_doc.has_vat_rates():
            # Total.
            name = [cfg_data.get_local_phrase(u'total')]
            number = acc_doc.get_price_total()
            contents.append((name, number, u"bold"))
            if acc_doc.has_holdbacks():
                name = [u"%s %s" % (cfg_data.get_local_phrase(u'including'),
                                    cfg_data.get_local_phrase(u'holdback')),]
                number = acc_doc.get_holdback_amount()
                contents.append((name, number, u"italic"))
        else:
            # Tax free total.
            name = [cfg_data.get_local_phrase(u'tf-total')]
            number = acc_doc.get_price_total()
            contents.append((name, number, u"regular"))
            # VAT amounts.
            for vat_rate in acc_doc.get_all_vat_rates():
                name = [u"%s %s%%"
                        % (cfg_data.get_local_phrase(u'vat-amount'),
                           format_number(vat_rate, ACCURACY,
                                                  cfg_data.number_separators))]
                number = acc_doc.get_vat_amount_for_rate(vat_rate)
                contents.append((name, number, u"regular"))
            # Including taxes total.
            name = [cfg_data.get_local_phrase(u'it-total')]
            number = acc_doc.get_including_taxes_total()
            contents.append((name, number, u"bold"))
            if acc_doc.has_holdbacks():
                name = [u"%s %s" % (cfg_data.get_local_phrase(u'including'),
                                    cfg_data.get_local_phrase(u'holdback')),
                        cfg_data.get_local_phrase(u'on-tf')]
                number = acc_doc.get_holdback_amount()
                contents.append((name, number, u"italic"))
                if acc_doc.has_vat_holdbacks():
                    name = [u"%s %s" % (cfg_data.get_local_phrase(u'including'),
                                        cfg_data.get_local_phrase(u'holdback')),
                            cfg_data.get_local_phrase(u'on-vat')]
                    number = acc_doc.get_holdback_vat_amount()
                    contents.append((name, number, u"italic"))
        return contents

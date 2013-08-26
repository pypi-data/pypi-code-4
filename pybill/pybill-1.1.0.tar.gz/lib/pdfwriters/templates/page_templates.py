# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.templates.page_templates`` module contains the
definition of the page template classes used in the PDF generation with
ReportLab `platypus`.

These classes are derived from platypus standard classes but are specific to
PyBill software. The page templates draw the static content specific to the
accounting documents.

.. autoclass:: AccDocPageTemplate
   :show-inheritance:

.. autoclass:: AccDocFirstPageTemplate
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from locale import getdefaultlocale
from traceback import format_exc
import logging

from reportlab.lib.units import cm
from reportlab.lib.colors import black

from reportlab.platypus import Paragraph, Spacer, Image, Frame
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import PageTemplate, BaseDocTemplate

from pybill.lib.errors import PyBillReadingException, PyBillProcessingException
from pybill.lib.pdfwriters.utils import escape_text, format_number
from pybill.lib import ACCURACY
from pybill.lib.pdfwriters import (style_title, style_footer,
                                   style_normal_left, style_normal_right,
                                   style_little_left, style_little_right)


# Constant used to debug the result PDF (shows frame boundaries in the PDF).
SHOW_FRAMES_ON_PDF = False


class AccDocPageTemplate(PageTemplate):
    """
    Class defining the page template used to draw the other pages of accounting
    PDF documents (not the first one).

    This page template has a main frame that will be filled with the accounting
    table, and various other frames containing the logo, and the footer that are
    displayed identically on each page (static content).
    
    This page template can only be used with a document created from the
    :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
    document template. It contains some methods for writing the carry forward
    computed in this document template.

    .. attribute:: acc_doc
    
       Attribute containing the accounting entity thate describes the actual
       document to be rendered in PDF.
                   
       type: :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

    .. automethod:: __init__

    .. automethod:: _create_main_frame

    .. automethod:: beforeDrawPage

    .. automethod:: afterDrawPage

    .. automethod:: _draw_static_content

    .. automethod:: _draw_top_carry_forward

    .. automethod:: _draw_bottom_carry_forward
    """
    def __init__(self, acc_doc, template_id=""):
        """
        Initializes an ``AccDocPageTemplate`` object.

        :parameter acc_doc: Accounting entity containing the actual document
                            to be rendered in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :parameter template_id: identifier (name) of the page template.
        :type template_id: :class:`str`
        """
        self.acc_doc = acc_doc
        # Defines the main frame in which the accounting table will be
        # displayed.
        main_f = self._create_main_frame()
        # Calls the base class initializer.
        PageTemplate.__init__(self, id=template_id, frames=[main_f])
    
    def _create_main_frame(self):
        """
        Creates the main frame of the page template, in which the flow,
        generated from the accounting entity, will be displayed.
        
        :returns: The frame in which the PDF flow will be rendered.
        :rtype: :class:`reportlab.platypus.Frame`
        """
        main_f = Frame(1*cm, 4.5*cm, 19*cm, 18.3*cm,
                       leftPadding=0*cm, bottomPadding=0*cm,
                       rightPadding=0*cm, topPadding=0*cm, 
                       showBoundary=SHOW_FRAMES_ON_PDF)
        return main_f

    def beforeDrawPage(self, canvas, document):
        """
        Overrides the method called before drawing a new page of the PDF
        document.

        This method draws various static data on the page (logo, company
        address, footer, page number, carry forward from previous page).
        
        :parameter canvas: Canvas of the page where the content can be written.
        :type canvas: :class:`reportlab.pdfgen.canvas.Canvas`
        
        :parameter document:
            PDF Document created from a template. This document contains various
            useful information such as the page number or the carry forward.
        :type document:
            :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        """
        # Saves canvas state.
        canvas.saveState()
        self._draw_static_content(canvas, document)
        if document.display_carry_forward:
            self._draw_top_carry_forward(canvas, document)
        # Puts back the canvas in its previous state.
        canvas.restoreState()

    def afterDrawPage(self, canvas, document):
        """
        Overrides the method called after drawing a page of the PDF document.

        This method draws the carry forward to be brought forward to the next
        page.

        :parameter canvas: Canvas of the page where content can be written.
        :type canvas: `reportlab.pdfgen.canvas.Canvas`
        
        :parameter canvas: Canvas of the page where the content can be written.
        :type canvas: :class:`reportlab.pdfgen.canvas.Canvas`
        
        :parameter document:
            PDF Document created from a template. This document contains various
            useful information such as the page number or the carry forward.
        :type document:
            :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        """
        # Saves canvas state.
        canvas.saveState()
        if document.display_carry_forward:
            self._draw_bottom_carry_forward(canvas, document)
        # Puts back the canvas in its previous state.
        canvas.restoreState()

    def _draw_static_content(self, canvas, document):
        """
        Draws on the PDF page the static content that is displayed on all
        pages, i.e. logo, company address, footer, page number.

        :parameter canvas: Canvas of the page where the content can be written.
        :type canvas: :class:`reportlab.pdfgen.canvas.Canvas`
        
        :parameter document:
            PDF Document created from a template. This document contains various
            useful information such as the page number.
        :type document:
            :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        """
        cfg_data = self.acc_doc.cfg_data
        # Draws the logo.
        if cfg_data.company_logo: 
            # The logo is not drawn through a frame because images as flowables
            # cannot be aligned on the left (they are always centered).
            # The logo filename is converted to a string (no unicode!)
            if cfg_data.company_logo.__class__ is unicode:
                logo_filename = cfg_data.company_logo.encode(
                                                        getdefaultlocale()[1])
            else:
                logo_filename = cfg_data.company_logo
            try:
                img = Image(logo_filename)
            except IOError, exc:
                raise PyBillReadingException("Can't open logo file '%s'.\n%s"
                                        % (logo_filename, format_exc(limit=1)))
            img_height  = 1.8*cm
            img_width = img_height * img.drawWidth / img.drawHeight
            canvas.drawInlineImage(logo_filename,
                                   1*cm, 26.9*cm, img_width, img_height)
        else:
            # If there is no logo, writes the company name.
            if cfg_data.company_address.name:
                name_f = Frame(1*cm, 26.9*cm, 8.5*cm, 1.8*cm,
                               leftPadding=0*cm, bottomPadding=0*cm,
                               rightPadding=0*cm, topPadding=0*cm, 
                               showBoundary=SHOW_FRAMES_ON_PDF)
                f_content = [Paragraph(u"<b>%s</b>"
                                  % escape_text(cfg_data.company_address.name),
                                                style_title)]
                name_f.addFromList(f_content, canvas)
                if len(f_content) > 0:
                    text = (u"The name of the sending company ('%s') is too "
                            u"long and can't be displayed in the PDF."
                             % cfg_data.company_address.name)
                    raise PyBillProcessingException(
                                     text.encode("ascii", "xmlcharrefreplace"))
        # Draws the company address in a dedicated frame.
        company_f = Frame(1*cm, 22.9*cm, 8.5*cm, 3.9*cm,
                          leftPadding=0*cm, bottomPadding=0*cm,
                          rightPadding=0*cm, topPadding=0*cm, 
                          showBoundary=SHOW_FRAMES_ON_PDF)
        f_content = []
        for line in cfg_data.company_address.get_postal_address_lines():
            f_content.append(Paragraph(escape_text(line),
                                       style_normal_left))
        if cfg_data.company_address.phone != u"":
            text = u"%s%s %s" % (cfg_data.get_local_phrase(u'phone-kw'),
                                 cfg_data.get_local_phrase(u'colon'),
                                 cfg_data.company_address.phone)
            f_content.append(Paragraph(escape_text(text), style_little_left))
        if cfg_data.company_address.fax != u"":
            text = u"%s%s %s" % (cfg_data.get_local_phrase(u'fax-kw'),
                                 cfg_data.get_local_phrase(u'colon'),
                                 cfg_data.company_address.fax)
            f_content.append(Paragraph(escape_text(text), style_little_left))
        if cfg_data.company_address.web != u"":
            text = u"%s%s %s" % (cfg_data.get_local_phrase(u'web-kw'),
                                 cfg_data.get_local_phrase(u'colon'),
                                 cfg_data.company_address.web)
            f_content.append(Paragraph(escape_text(text), style_little_left))
        if cfg_data.company_address.email != u"":
            text = u"%s%s %s" % (cfg_data.get_local_phrase(u'email-kw'),
                                 cfg_data.get_local_phrase(u'colon'),
                                 cfg_data.company_address.email)
            f_content.append(Paragraph(escape_text(text), style_little_left))
        company_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("The address of the sending company is too long and can't "
                    "be entirely displayed in the PDF. The following lines "
                    "are not displayed:\n")
            for para in f_content:
                text += "  %s\n" % para.text
            raise PyBillProcessingException(
                                     text.encode("ascii", "xmlcharrefreplace"))
        # Draws the footer data (actually the company address) in a
        # dedicated frame.
        footer_f = Frame(3*cm, 1*cm, 15*cm, 2*cm,
                         leftPadding=0*cm, bottomPadding=0*cm,
                         rightPadding=0*cm, topPadding=0*cm, 
                         showBoundary=SHOW_FRAMES_ON_PDF)
        f_content = []
        for line in [l for l in cfg_data.footer_lines if l != u""]:
            string = u"<i>%s</i>" % escape_text(line)
            f_content.append(Paragraph(string, style_footer))
        footer_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("The footer is too long and can't be entirely displayed "
                    "in the PDF. The following lines are not displayed:\n")
            for para in f_content:
                text += "  %s\n" % para.text
            raise PyBillProcessingException(
                                     text.encode("ascii", "xmlcharrefreplace"))
        # Draws the header data (document reference and page number) in a
        # dedicated frame.
        pagenum_f = Frame(12.5*cm, 27.7*cm, 7.5*cm, 1*cm,
                          leftPadding=0*cm, bottomPadding=0*cm,
                          rightPadding=0*cm, topPadding=0*cm,
                          showBoundary=SHOW_FRAMES_ON_PDF)
        if self.acc_doc.doc_ref.strip() != u"":
            text = u"%s - " % self.acc_doc.doc_ref.strip()
        else:
            text = u""
        text += u"Page %d" % document.page
        f_content = [Paragraph(escape_text(text, True),
                               style_little_right)]
        pagenum_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("The document reference ('%s') is too long and can't be "
                    "displayed in the PDF (in page header)." 
                    % self.acc_doc.doc_ref)
            raise PyBillProcessingException(
                                     text.encode("ascii", "xmlcharrefreplace"))

    def _draw_top_carry_forward(self, canvas, document):
        """
        Draws on the PDF page the carry forward that is brought forward from
        the previous page.

        This carry forward is displayed at the top of the page just before the
        main frame.

        :parameter canvas: Canvas of the page where the content can be written.
        :type canvas: :class:`reportlab.pdfgen.canvas.Canvas`
        
        :parameter document:
            PDF Document created from a template. This document contains various
            useful information such as the carry forward.
        :type document:
            :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        """
        cfg_data = self.acc_doc.cfg_data
        c_fwd_f = Frame(12.5*cm, 23*cm, 7.5*cm, 0.8*cm,
                        leftPadding=0*cm, bottomPadding=0*cm,
                        rightPadding=0*cm, topPadding=0*cm,
                        showBoundary=SHOW_FRAMES_ON_PDF)
        # Builds the cells list for the carry forward table (1 line, 2 cols).
        cf_table_data = [[]]
        cf_table_data[0].append(Paragraph(
                      escape_text(cfg_data.get_local_phrase(u'carry-forward')),
                                          style_normal_left))
        cf_table_data[0].append(Paragraph(
                                format_number(document.carry_forward, ACCURACY,
                                              cfg_data.number_separators),
                                          style_normal_right))
        # Builds the carry forward table (with its style).
        cf_table = Table(cf_table_data, [4.5*cm, 3*cm], None)
        cf_table.setStyle(
            TableStyle([ ('ALIGN',     (0,0),( 0,-1), 'LEFT'),
                         ('ALIGN',     (1,0),( 1,-1), 'RIGHT'),
                         ('VALIGN',    (0,0),(-1,-1), 'TOP'),
                         ('INNERGRID', (0,0),(-1,-1), 0.25, black),
                         ('BOX',       (0,0),(-1,-1), 0.5, black),
                       ])
            )
        f_content = [cf_table]
        c_fwd_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("The carry forward can't be displayed in the PDF, on the "
                    "top of the page (lacking space).")
            raise PyBillProcessingException(
                                     text.encode("ascii", "xmlcharrefreplace"))

    def _draw_bottom_carry_forward(self, canvas, document):
        """
        Draws on the PDF page the carry forward that is brought forward to
        the next page.

        This carry forward is displayed at the bottom of the page just after the
        main frame.

        :parameter canvas: Canvas of the page where the content can be written.
        :type canvas: :class:`reportlab.pdfgen.canvas.Canvas`
        
        :parameter document:
            PDF Document created from a template. This document contains various
            useful information such as the page number.
        :type document:
            :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        """
        cfg_data = self.acc_doc.cfg_data
        c_fwd_f = Frame(12.5*cm, 3.5*cm, 7.5*cm, 0.8*cm,
                        leftPadding=0*cm, bottomPadding=0*cm,
                        rightPadding=0*cm, topPadding=0*cm,
                        showBoundary=SHOW_FRAMES_ON_PDF)
        # Builds the cells list for the carry forward table (1 line, 2 cols).
        cf_table_data = [[]]
        cf_table_data[0].append(Paragraph(
                   escape_text(cfg_data.get_local_phrase(u'to-bring-forward')),
                                          style_normal_left))
        cf_table_data[0].append(Paragraph(
                                format_number(document.carry_forward, ACCURACY,
                                              cfg_data.number_separators),
                                          style_normal_right))
        # Builds the carry forward table (with its style).
        cf_table = Table(cf_table_data, [4.5*cm, 3*cm], None)
        cf_table.setStyle(
            TableStyle([ ('ALIGN',     (0,0),( 0,-1), 'LEFT'),
                         ('ALIGN',     (1,0),( 1,-1), 'RIGHT'),
                         ('VALIGN',    (0,0),(-1,-1), 'TOP'),
                         ('INNERGRID', (0,0),(-1,-1),  0.25, black),
                         ('BOX',       (0,0),(-1,-1),  0.5, black),
                       ])
            )
        f_content = [cf_table]
        c_fwd_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("The carry forward can't be displayed in the PDF, on the "
                    "bottom of the page (lacking space).")
            raise PyBillProcessingException(
                                     text.encode("ascii", "xmlcharrefreplace"))


class AccDocFirstPageTemplate(AccDocPageTemplate):
    """
    Class defining the page template used to draw the first pages of accounting
    documents in PDF.

    This page template has a main frame that will be filled
    with the accounting table, and various other frames containing the logo,
    the date, the address, the footer that are displayed identically on each
    page (static content).
    
    This template is a specialization of
    :class:`~pybill.lib.pdfwriters.templates.page_templates.AccDocPageTemplate`.
    
    This page template can only be used with a document created from the
    :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
    document template. It contains some methods for writing the carry forward
    computed in this document template.

    .. automethod:: __init__
        
    .. automethod:: _create_main_frame
        
    .. automethod:: beforeDrawPage
        
    .. automethod:: _draw_specific_static_content
    """
    def __init__(self, acc_doc, template_id=""):
        """
        Initializes an ``AccDocFirstPageTemplate`` object.

        :parameter acc_doc: Accounting entity containing the actual document
                            to be rendered in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :parameter template_id: identifier (name) of the page template.
        :type template_id: :class:`str`
        """
        AccDocPageTemplate.__init__(self, acc_doc, template_id=template_id)

    def _create_main_frame(self):
        """
        Creates the main frame of the page template, in which the flow,
        generated from the accounting entity, will be displayed.

        The main frame on the first page is littler than on the other pages as
        there is more static content on the first page (addresses, etc.)
        
        :returns: The frame in which the PDF flow will be rendered.
        :rtype: :class:`reportlab.platypus.Frame`
       """
        main_f = Frame(1*cm, 4.5*cm, 19*cm, 13.3*cm,
                       leftPadding=0*cm, bottomPadding=0*cm,
                       rightPadding=0*cm, topPadding=0*cm, 
                       showBoundary=SHOW_FRAMES_ON_PDF)
        return main_f

    def beforeDrawPage(self, canvas, document):
        """
        Overrides the method called before drawing a new page of the PDF
        document.

        This method draws various static data on the page (logo, company
        address, footer, page number, carry forward from previous page).
        
        :parameter canvas: Canvas of the page where the content can be written.
        :type canvas: :class:`reportlab.pdfgen.canvas.Canvas`
        
        :parameter document:
            PDF Document created from a template. This document contains various
            useful information such as the page number.
        :type document:
            :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        """
        # Saves canvas state.
        canvas.saveState()
        self._draw_static_content(canvas, document)
        self._draw_specific_static_content(canvas, document)
        # Puts back the canvas in its previous state.
        canvas.restoreState()

    def _draw_specific_static_content(self, canvas, document):
        """
        Draws on the PDF page some specific static content that is displayed
        on each page based on this template (in fact, only the first page).
        
        This specific static content is document metadata, receiver address,
        and date.
        
        :parameter canvas: Canvas of the page where the content can be written.
        :type canvas: :class:`reportlab.pdfgen.canvas.Canvas`
        
        :parameter document:
            PDF Document created from a template. This document contains various
            useful information such as the page number.
        :type document:
            :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate`
        """
        cfg_data = self.acc_doc.cfg_data
        # Draws the metadata (document various references) in a dedicated
        # frame.
        metad_f = Frame(1*cm, 19.95*cm, 8.5*cm, 2.75*cm, 
                        leftPadding=0*cm, bottomPadding=0*cm,
                        rightPadding=0*cm, topPadding=0*cm, 
                        showBoundary=SHOW_FRAMES_ON_PDF)
        f_content = []
        if self.acc_doc.doc_ref.strip() != u"":
            text = u"%s%s %s" % (cfg_data.get_local_phrase(u'doc-ref-kw'),
                                 cfg_data.get_local_phrase(u'colon'),
                                 self.acc_doc.doc_ref.strip())
            f_content.append(Paragraph(escape_text(text, True),
                                       style_little_left))
        for kw, val in [(k, v) for k, v in self.acc_doc.other_infos.items()
                        if (k.strip() != u"" or v.strip() != u"")]:
            text = u"%s%s %s" % (kw.strip(),
                                 cfg_data.get_local_phrase('colon'),
                                 val.strip())
            f_content.append(Paragraph(escape_text(text, True),
                                       style_little_left))
        metad_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("There is too many metadata information in document. The "
                    "following items can't be displayed in the PDF:\n")
            for para in f_content:
                text += "  %s\n" % para.text
            logging.warning(text.encode("ascii", "xmlcharrefreplace"))
        # Draws the receiver company address in a dedicated frame.
        address_f = Frame(9.8*cm, 21.85*cm, 9.7*cm, 3.7*cm,
                          leftPadding=0*cm, bottomPadding=0*cm,
                          rightPadding=0*cm, topPadding=0*cm, 
                          showBoundary=SHOW_FRAMES_ON_PDF)
        f_content = []
        if self.acc_doc.receiver.organisation:
            text = self.acc_doc.receiver.organisation.name.strip()
            if text != u"":
                f_content.append(Paragraph(u"<b>%s</b>" 
                                           % escape_text(text, True),
                                           style_normal_left))
            for div in [d.strip() for d
                        in self.acc_doc.receiver.organisation.divisions
                        if d.strip() != u""]:
                f_content.append(Paragraph(escape_text(div, True),
                                           style_normal_left))
            for line in \
                 self.acc_doc.receiver.organisation.get_postal_address_lines():
                f_content.append(Paragraph(escape_text(line, True),
                                           style_normal_left))
        else:
            text = self.acc_doc.receiver.get_person_name()
            if text != u"":
                f_content.append(Paragraph(u"<b>%s</b>" 
                                           % escape_text(text, True),
                                           style_normal_left))
            for line in self.acc_doc.receiver.get_postal_address_lines():
                f_content.append(Paragraph(escape_text(line, True),
                                           style_normal_left))
        address_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("The receiver's address is too long and can't be entirely "
                    "displayed in the PDF. The following lines are not "
                    "displayed:\n")
            for para in f_content:
                text += "  %s\n" % para.text
            logging.warning(text.encode("ascii", "xmlcharrefreplace"))
        # Draws the sender, receiver, date and place in a dedicated frame.
        date_f = Frame(1*cm, 17.9*cm, 19*cm, 1.95*cm,
                       leftPadding=0*cm, bottomPadding=0*cm,
                       rightPadding=0*cm, topPadding=0*cm, 
                       showBoundary=SHOW_FRAMES_ON_PDF)
        f_content = []
        if self.acc_doc.receiver.get_person_name() != u"":
            text = u"%s%s <b>%s</b>"\
                 % (escape_text(cfg_data.get_local_phrase(u'receiver-kw')),
                    escape_text(cfg_data.get_local_phrase(u'colon')),
                    escape_text(self.acc_doc.receiver.get_person_name(), True))
            if self.acc_doc.receiver.organisation:
                for job_t in [j.strip() for j
                              in self.acc_doc.receiver.organisation.job_titles
                              if j.strip() != u""]:
                    text += u" - %s" % escape_text(job_t, True)
            f_content.append(Paragraph(text, style_little_left))
        if (self.acc_doc.sender is not None and 
            self.acc_doc.sender.get_person_name() != u""):
            text = u"%s%s <b>%s</b>" \
                   % (escape_text(cfg_data.get_local_phrase(u'sender-kw')),
                      escape_text(cfg_data.get_local_phrase(u'colon')),
                      escape_text(self.acc_doc.sender.get_person_name(), True))
            if self.acc_doc.sender.phone.strip() != u"":
                text += u" - %s" % escape_text(self.acc_doc.sender.phone, True)
            if self.acc_doc.sender.email.strip() != u"":
                text += u" - %s" % escape_text(self.acc_doc.sender.email, True)
            f_content.append(Paragraph(text, style_little_left))
        f_content.append(Spacer(1, 0.2*cm))
        text = u"%s, %s %s" % (self.acc_doc.place.strip(),
                               cfg_data.get_local_phrase(u'on-date'),
                               self.acc_doc.date)
        f_content.append(Paragraph(escape_text(text, True),
                                   style_normal_right))
        date_f.addFromList(f_content, canvas)
        if len(f_content) > 0:
            text = ("The date, the sender's name and the receiver's name "
                    "be displayed in the PDF, on the top of the first page "
                    "(lacking space).")
            raise PyBillProcessingException(
                                     text.encode("ascii", "xmlcharrefreplace"))

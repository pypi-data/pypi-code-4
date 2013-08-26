# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.writers`` module defines the public class that can
generate a PDF file for the accounting documents.

The PDF generation uses the platypus machinery of ReportLab and is, of course,
based on PyBill flow generators and templates.

.. autoclass:: PDFWriter
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from traceback import format_exc

from pybill.lib.errors import PyBillProcessingException

from pybill.lib.pdfwriters.templates import AccDocDocumentTemplate
from pybill.lib.pdfwriters.flowgenerators import (BillFlowGenerator,
                                                  ClaimFormFlowGenerator,
                                                  DownpaymentFlowGenerator,
                                                  ProFormaFlowGenerator,
                                                  DebitFlowGenerator)


class PDFWriter:
    """
    Class writing the PDF for all kinds of accounting documents.

    This class uses flow generators that are specific to the kind of accounting
    document to be rendered in PDF (bill, claim form, debit, downpayment,
    pro-forma). In order to prevent the instantiation of several generators of
    the same class, one flow generator of each class is kept in an attribute.

    .. attribute:: flow_generators

        Attribute containing a dictionary of flow generator objects indexed with
        the name of the class of the accounting documents they can transform in
        PDF. This dictionary contains all the specialized flow generators that
        can be used by this writer.

        type: Dictionary of :class:`~pybill.lib.pdfwriters.flowgenerators.abstract.AbstractFlowGenerator`
        objects indexed with unicode keys

    .. automethod:: __init__
    """

    def __init__(self):
        """
        Initializes a `PDFWriter` object and fills the ``flow_generators``
        attributes with the correct generator objects
        """
        self.flow_generators = {
            'Bill': BillFlowGenerator(),
            'ClaimForm': ClaimFormFlowGenerator(),
            'ProForma': ProFormaFlowGenerator(),
            'Downpayment': DownpaymentFlowGenerator(),
            'Debit' : DebitFlowGenerator(),
            }

    def write(self, acc_doc, pdf_file):
        """
        Writes a PDF file for an accounting document.

        :parameter acc_doc:
            Accounting document that must be transformed in PDF. This document
            contains the configuration object that will be used during this
            transform (a configuration object contains numerous useful pieces of
            data).

        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :parameter pdf_file:
            Name of the file where the PDF will be written in.
        :type pdf_file: unicode
        """
        try:
            flow_gen = self.flow_generators[acc_doc.__class__.__name__]
        except KeyError:
            raise PyBillProcessingException("Unexpected class of accounting "
                                            "document (%s) that can't be "
                                            "rendered in PDF."
                                            % acc_doc.__class__.__name__)
        try:
            # Opens a new PDF document from the PyBill-specific template
            pdf_doc = AccDocDocumentTemplate(pdf_file, acc_doc)
            # Fills it with the content returned by the flow generator
            pdf_doc.build(flow_gen.generate_flow(acc_doc))
        except IOError, exc:
            raise PyBillProcessingException("Unable to write PDF result in "
                                   "%s.\n%s" % (pdf_file, format_exc(limit=1)))

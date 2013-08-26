# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.flowgenerators`` sub-package contains the definition of
the flow generation classes used in the PDF generation with ReportLab
`platypus`.

These classes generate the flow content of a bill, a claim form, a downpayment,
a pro-forma or a debit: title, various paragraphes, main table detailling the
items, and total table. This flow content will be displayed on various pages by
the :class:`~pybill.lib.pdfwriters.templates.doc_templates.AccDocDocumentTemplate``
document template thanks to the platypus machinery.

The sub-package is divided in several modules, each defining one of the flow
generator.

``abstract`` module
===================

.. automodule:: pybill.lib.pdfwriters.flowgenerators.abstract

``bill_generator`` module
=========================

.. automodule:: pybill.lib.pdfwriters.flowgenerators.bill_generator

``claimform_generator`` module
==============================

.. automodule:: pybill.lib.pdfwriters.flowgenerators.claimform_generator

``debit_generator`` module
==========================

.. automodule:: pybill.lib.pdfwriters.flowgenerators.debit_generator

``downpayment_generator`` module
================================

.. automodule:: pybill.lib.pdfwriters.flowgenerators.downpayment_generator

``proforma_generator`` module
=============================

.. automodule:: pybill.lib.pdfwriters.flowgenerators.proforma_generator
"""
__docformat__ = "restructuredtext en"

# Imports the classes exported by this package.

from pybill.lib.pdfwriters.flowgenerators.bill_generator import \
                                                              BillFlowGenerator
from pybill.lib.pdfwriters.flowgenerators.claimform_generator import \
                                                         ClaimFormFlowGenerator
from pybill.lib.pdfwriters.flowgenerators.downpayment_generator import \
                                                       DownpaymentFlowGenerator
from pybill.lib.pdfwriters.flowgenerators.debit_generator import \
                                                             DebitFlowGenerator
from pybill.lib.pdfwriters.flowgenerators.proforma_generator import \
                                                          ProFormaFlowGenerator

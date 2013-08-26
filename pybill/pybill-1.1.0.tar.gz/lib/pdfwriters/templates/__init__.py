# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.templates`` sub-package contains the definition of the
template classes (page templates and document template) used in the PDF
generation with ReportLab `platypus`.

The page templates describe the structure of the PDF pages and where the flow
content can be written. The document template describes a PDF document, mainly
explaining which page templates will be used. Both templates are used by the
platypus machinery to display, into the PDF documents, the flowables generated
by the :mod:`pybill.lib.pdfwriters.flowables` flow generators.

The sub-package is divided in several modules, each defining one type of
template.

``page_templates`` module
=========================

.. automodule:: pybill.lib.pdfwriters.templates.page_templates

``doc_templates`` module
========================

.. automodule:: pybill.lib.pdfwriters.templates.doc_templates
"""
__docformat__ = "restructuredtext en"


# Imports the classes that are exported from this package
from pybill.lib.pdfwriters.templates.page_templates import (AccDocPageTemplate,
                                                       AccDocFirstPageTemplate)
from pybill.lib.pdfwriters.templates.doc_templates import AccDocDocumentTemplate

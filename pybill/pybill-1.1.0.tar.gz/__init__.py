# -*- coding: utf-8 -*-
"""
PyBill is a software that can transform an XML description of accounting
documents (such as bills, claim forms, debits or downpayments) into PDF
printable documents.

The XML documents are defined into the `PyBill Document 1.0` format.
Configuration files also described in XML allow to have different renderings
(logo, sender address and internationalization). The chosen configuration can be
set into a processing instruction in the XML accounting document.

PyBill uses :mod:`lxml` library to read and write the XML files, and
:mod:`reportlab` library to produce the PDFs.
"""
__docformat__ = "restructuredtext en"

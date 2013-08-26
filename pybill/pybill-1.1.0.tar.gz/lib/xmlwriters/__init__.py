# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlwriters`` package contains the classes and functions that
PyBill accounting entities in XML files.

Currently, PyBill just knows how to dump the entities in the
`PyBill Document 1.0` format. There is no support for writing the entities in
the old formats.

The :func:`write_accounting_doc` is the public function that should be used from
the outside of this package. The :const:`ENCODING` constant is also public and
contains the default encoding used for all the XML files written by PyBill. They
are both imported and available in the namespace of this package.
"""
__docformat__ = "restructuredtext en"


# Imports the constants and functions that must be used from the outside.
from pybill.lib.xmlwriters.utils import ENCODING
from pybill.lib.xmlwriters.accdoc import write_accounting_doc

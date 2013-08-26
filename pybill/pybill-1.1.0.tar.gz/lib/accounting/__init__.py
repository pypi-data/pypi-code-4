# -*- coding: utf-8 -*-
"""
``pybill.lib.accounting`` package contains the classes used to generate the
accounting entries from the accounting documents processed by PyBill.

The accounting entries can be saved in an XML file in `pycompta` format. This
package uses :mod:`lxml` to generate and write the XML data.

The only public class that should be used outside of this package is the
:class:`~pybill.lib.accounting.generator.EntriesGenerator` class. This class is
imported and available in the namespace of this package. Some useful constants
used to designate account numbers are also imported and available in the
namespace of this package.
"""
__docformat__ = "restructuredtext en"


# Imports exported classes and constants.

from pybill.lib.accounting.utils import CLIENT, CLIENT_HOLDBACK, PRODUCT, VAT
from pybill.lib.accounting.generator import EntriesGenerator

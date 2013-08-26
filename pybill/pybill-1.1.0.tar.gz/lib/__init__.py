# -*- coding: utf-8 -*-
"""
``pybill.lib`` package is the library package of `PyBill`.

It contains all the core code of PyBill for reading and writing XML accounting
documents, computing each type of accounting document, writing PDF
representations of the accounting documents, and writing accounting entries.

The ``pybill.lib`` package directly contains the definitions of some constants
used all over `PyBill` code.

.. autodata:: ACCURACY

.. autodata:: PBD_1_0

.. autodata:: PBD_0_X

.. autodata:: PBD_FORMATS

.. autodata:: PBD_XMLNS

.. autodata:: PBC_1_0

.. autodata:: PBC_0_X

.. autodata:: PBC_FORMATS

.. autodata:: PBC_XMLNS
"""
__docformat__ = "restructuredtext en"

ACCURACY = 2
"""
Constant defining the accuracy of all the computations that will be done in
PyBill.

When computing the total of an item, it will be rounded at this accuracy. When
computing the total of an accounting document, the rounded total of each item
will be used and the result will be rounded at this accuracy.

type: :class:`int`

value: ``2``
"""

PBD_1_0 = u"PBD-1.0"
"""
Constant representing the format `PyBill Document 1.0`.

This constant is used for the format specification in the XML document files.

type: :class:`unicode`

value: ``PBD-1.0``
"""

PBD_0_X = u"PBD-0.X"
"""
Constant representing the older format `PyBill Document 0.X`.

This constant is used for the format specification in the XML document files.

type: :class:`unicode`

value: ``PBD-0.X``
"""

PBD_FORMATS = [PBD_1_0, PBD_0_X]
"""
Constant containing the list of the possible formats for the documents
(using the constants previously defined).

type: list of :class:`unicode`

definition: ``[PBD_1_0, PBD_0_X]``
"""

PBD_XMLNS = u"http://www.logilab.org/2010/PyBillDocument"
"""
Constant defining the namespace used for PyBill XML document in
`PyBill Document 1.0` format or higher.

type: :class:`unicode`

value: ``http://www.logilab.org/2010/PyBillDocument``
"""

PBC_1_0 = u"PBC-1.0"
"""
Constant representing the format `PyBill Configuration 1.0`.

This constant is used for the format specification in the XML configuration
files.

type: :class:`unicode`

value: ``PBC-1.0``
"""

PBC_0_X = u"PBC-0.X"
"""
Constant representing the older format `PyBill Configuration 0.X`.

This constant is used for the format specification in the XML configuration
files.

type: :class:`unicode`

value: ``PBC-0.X``
"""

PBC_FORMATS = [PBC_1_0, PBC_0_X]
"""
Constant containing the list of the possible formats for the configuration
(using the constants previously defined).

type: list of :class:`unicode`

definition: ``[PBC_1_0, PBC_0_X]``
"""

PBC_XMLNS = u"http://www.logilab.org/2010/PyBillConfig"
"""
Constant defining the namespace used for PyBill XML configuration in
`PyBill Config 1.0` format or higher.

type: :class:`unicode`

value: ``http://www.logilab.org/2010/PyBillConfig``
"""

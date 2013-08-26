# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlreaders`` package contains the classes and functions used to
read the XML files describing the accounting documents and to build the
corresponding entity objects.

This package contains classes to read XML files either in the
`PyBill Document 0.X` old format or in the `PyBill Document 1.0` latest format.
It also defines the public
:class:`~pybill.lib.xmlreaders.accdoc.AccDocXMLReader` class that manages
the reading of an XML file whatever its PBD format is. This public class is the
only class that should be used from the outside of this package. It is imported
and available in the namespace of this package.
"""
__docformat__ = "restructuredtext en"

# Imports the classes and constants that must be used from the outside.
from pybill.lib.xmlreaders.accdoc import AccDocXMLReader


# -*- coding: utf-8 -*-
"""
``pybill.lib.xmlwriters.accdoc`` module contains the function used for saving
PyBill accounting documents into XML files.

The XML files are built thanks to :mod:`lxml` library. All the type of
accountind documents (bill, claim-form, debit, downpayment, pro-forma) can be
saved by this function.

Currently, it is only possible to save the entities in the latest
`PyBill Document 1.0` format.

.. autofunction:: write_accounting_doc
"""
__docformat__ = "restructuredtext en"

from lxml import etree

from pybill.lib import PBD_1_0
from pybill.lib.errors import PyBillWritingException

from pybill.lib.xmlwriters.utils import ENCODING, open_xml_outfile
from pybill.lib.xmlwriters.accdoc_format_1_0 import write_accdoc_1_0_xml


def write_accounting_doc(acc_doc, xml_file, format=PBD_1_0, encoding=ENCODING):
    """
    Writes an accounting entity into an XML file in ``format`` PyBill format.

    If the entity is linked to a configuration object that has a reference, a
    processing instruction will be added in the XML in order to specify
    the configuration to be used.

    This function relies on the other functions defined in this package that
    know how to write the XML corresponding to a given format.

    :parameter acc_doc: PyBill entity describing the accounting document to
                        be saved in XML. Can be a ``Bill``, a ``ClaimForm``,
                        a ``Debit``, a ``Downpayment`` or a ``ProForma``
                        object.
    :type acc_doc: :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

    :parameter xml_file: Name of the file where the XML has to be saved.
    :type xml_file: :class:`unicode`

    :parameter format: name of the PyBill format used for the XML. Currently,
                       only `PyBill Document 1.0` format is supported; therefore
                       the only possible value for this parameter is
                       ``u"PBD-1.0"``.
    :type format: :class:`unicode`

    :parameter encoding: Encoding used to write the XML file.
    :type encoding: :class:`str`
    """
    if format == PBD_1_0:
        root_elt = write_accdoc_1_0_xml(acc_doc)
    else:
        raise PyBillWritingException("Format '%s' is not currently supported "
                                     "by the XML writer." % format)        
    out = open_xml_outfile(xml_file, encoding=encoding)
    # If the accounting document is linked to a configuration, writes a
    # processing instruction in the XML file.
    if (acc_doc.cfg_data is not None and acc_doc.cfg_data.name):
        cfg_pi = etree.ProcessingInstruction(u"pybill",
                                        u'config="%s"' % acc_doc.cfg_data.name)
        out.write(etree.tostring(cfg_pi, encoding=encoding, 
                                 pretty_print=True, xml_declaration=False))
        out.write("\n")
    # Finally, writes the XML elements.
    out.write(etree.tostring(root_elt, encoding=encoding, 
                             pretty_print=True, xml_declaration=False))

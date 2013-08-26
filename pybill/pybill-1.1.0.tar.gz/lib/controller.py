# -*- coding: utf-8 -*-
"""
``pybill.lib.controller`` module defines the main controller of PyBill.

This controller knows how to read the XML accounting documents and how to
produce PDF, using the other classes that exist in the ``pybill.lib`` module.

.. autoclass:: PyBillController
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

import os
import os.path as osp

from pybill.lib import PBD_1_0

from pybill.lib.config import ConfigRegister
from pybill.lib.xmlreaders import AccDocXMLReader
from pybill.lib.pdfwriters import PDFWriter
from pybill.lib.xmlwriters import write_accounting_doc
from pybill.lib.accounting.generator import EntriesGenerator


class PyBillController:
    """
    Main controller that implements all the operations available in PyBill
    software.

    This controller uses dedicated object for reading XML documents and
    producing PDF output.

    .. attribute:: config_register

        Attribute that contains a config register object. This object has got a
        library of config files read in the various config directories and can
        give the config data used by a given accounting entity.

        type: :class:`~pybill.lib.config.register.ConfigRegister`

    .. attribute:: accdoc_reader

        Attribute that contains an XML reader object. This object can read an
        XML file containing an accounting document, build the corresponding
        entity and give the name of the config file used by this entity.

        type: :class:`~pybill.lib.xmlreaders.accdoc.AccDocXMLReader`

    .. attribute:: pdf_writer

        Attribute that contains a PDF writer object. This object can produce a
        PDF file rendering an accounting entity.
        
        type: :class:`~pybill.lib.pdfwriters.writers.PDFWriter`

    .. attribute:: entries_generator

        Attribute containing an entries generator object. This object can export
        accounting entries corresponding to accounting entities into an XML
        file. The XML file is compatible with `pycompta` software.

        type: :class:`~pybill.lib.accounting.generator.EntriesGenerator`

    .. automethod:: __init__
    
    """
    def __init__(self):
        """
        Initializes a new ``PyBillController`` object.

        Builds the specialized objects that will be used during the operations.
        """
        self.config_register = ConfigRegister()
        self.accdoc_reader = AccDocXMLReader(self.config_register)
        self.pdf_writer = PDFWriter()
        self.entries_generator = EntriesGenerator()

    def build_entities_from_files(self, filenames, cfg_filename=None):
        """
        Builds the accounting entities from files containing XML data in
        PyBill Document formats (e.g. `PBD-1.0`).

        The names of the files are given in ``filenames`` list. The method
        returns a list of couples (accounting entity, base of filename where
        the entity was read).

        :parameter filenames: List of the names (strings) of the files that
                              contain accounting documents in XML PyBill
                              formats (e.g. `PBD-1.0`). These documents will
                              be read and stored as accounting entities
                              (``Bill`` objects, etc.)
        :type filenames: list of :class:`str`

        :parameter cfg_filename: Name of a file containing a configuration in
                                 XML format. When specified, this configuration
                                 will be used for all the accouting entities
                                 read from ``filenames`` files and will preempt
                                 any configuration specified in these files.
        :type cfg_filename: :class:`str`

        :returns: List of couples (accounting entity, base of filename where
                  this entity was read from). The accounting entity was built
                  from one of the file in ``filenames``. The base of filename
                  is the name of this file without its extension.
        :rtype:
            list of tuples (:class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`, :class:`str`)
        """
        entities = []
        if cfg_filename is not None:
            cfg_filename = osp.abspath(cfg_filename)
        for filename in filenames:
            in_filename = osp.abspath(filename)
            accdoc = self.accdoc_reader.load_data(in_filename, cfg_filename)
            entities.append((accdoc, osp.splitext(in_filename)[0]))
        return entities

    def save_entities_to_files(self, entities, xml_encoding):
        """
        Saves the accounting entities in some XML files in latest PyBill
        format (\ `PBD-1.0`\ ).

        Actually, the ``entities`` list consists in a list of couples
        (accounting entity, name of the file where to save the XML document).

        If the file where the XML will be saved already exists, it is copied
        into a `.old` file before the XML is saved.

        :parameter entities: List of couples composed of an accounting entity
                             (e.g. ``Bill`` object) and the name of the file
                             where the XML representation of this entity will
                             be saved in.
        :type entities:
            list of tuples (:class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`, :class:`str`)

        :parameter xml_encoding: Encoding used for writing the XML files
                                 describing the accounting entities.
        :type xml_encoding: :class:`str`
        """
        for accdoc, xml_filename in entities:
            if osp.exists(xml_filename):
                old_filename = "%s%sold" % (xml_filename, osp.extsep)
                if osp.exists(old_filename):
                    os.remove(old_filename)
                os.rename(xml_filename, old_filename)
            write_accounting_doc(accdoc, xml_filename, 
                                 format=PBD_1_0, encoding=xml_encoding)

    def write_pdf_to_files(self, entities):
        """
        Builds the PDF corresponding to accounting entities and saves them in
        files.

        Actually, the ``entities`` list consists in a list of couples
        (accounting entity, name of the file where to save the result of
        the PDF generation).

        :parameter entities: List of couples composed of an accounting entity
                             (e.g. ``Bill`` object) and the name of the file
                             where the PDF produced for this entity will be
                             saved in.
        :type entities:
            list of tuples (:class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`, :class:`str`)
        """
        for accdoc, pdf_filename in entities:
            self.pdf_writer.write(accdoc, pdf_filename)

    def export_accounting_entries_to_xml_file(self, entities, 
                                              filename, xml_encoding):
        """
        Builds accounting entries from the accounting entities and save them
        in an XML file.

        For this method, the ``entities`` list only consists in a list of
        accounting entities.

        :parameter entities: List of accounting entities (e.g. ``Bill``
                             object).
        :type entities:
            list of :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`

        :parameter filename: Name of the file where the XML accounting entries
                             will be saved in.
        :type filename: :class:`str`

        :parameter xml_encoding: Encoding used for writing the XML file
                                 containing the accounting entries.
        :type xml_encoding: :class:`str`
        """
        self.entries_generator.reset_entries()
        for accdoc in entities:
            self.entries_generator.generate_entry(accdoc)
        self.entries_generator.write_entries_in_xml(filename, 
                                                    encoding=xml_encoding)

# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from tempfile import mkdtemp
from shutil import copy
from os import remove, listdir, rmdir
from os import path as osp
from lxml import etree

from pybill.lib import PBD_XMLNS
from pybill.lib.entities.accounting_docs import Bill
from pybill.lib.xmlwriters.utils import ENCODING

from pybill.lib.controller import PyBillController


class FakeReader:
    """
    Class used to replace the real ``AccDocXMLReader``. We just need to
    checks the calls to the reader are correct.
    """
    def load_data(self, accdoc_file, cfg_file=None):
        """
        Fakes the data reading.
        """
        return "Read from %s with %s config" % (accdoc_file, cfg_file)


class FakeWriter:
    """
    Class used to replace the real ``PDFWriter``. We just need to
    check the calls to the writer are correct.
    """
    def __init__(self):
        self.writes = []

    def write(self, accdoc_entity, pdf_file):
        """
        Fakes the PDF building and writing.
        """
        self.writes.append("PDF write from %s in %s"
                           % (accdoc_entity, pdf_file))


class FakeEntriesGenerator:
    """
    Class used to replace the real ``EntriesGenerator``. We just need to
    check the calls to the generator are correct.
    """
    def __init__(self):
        self.actions = []

    def reset_entries(self):
        """
        Fakes the reset.
        """
        self.actions.append("Deletes all entries")
        
    def generate_entry(self, accdoc_entity):
        """
        Fakes the entry generation.
        """
        self.actions.append("Generates accounting entry for %s"
                            % accdoc_entity)

    def write_entries_in_xml(self, filename, encoding=ENCODING):
        """
        Fakes the XML writing.
        """
        self.actions.append("Writes entries in %s XML file in %s encoding" 
                            % (filename, encoding))



class ControllerTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class.
        """
        self.controller = PyBillController()
        self.controller.accdoc_reader = FakeReader()
        self.controller.pdf_writer = FakeWriter()
        self.controller.entries_generator = FakeEntriesGenerator()
        self.temp_dir = mkdtemp()

    def tearDown(self):
        for fname in listdir(self.temp_dir):
            remove(osp.join(self.temp_dir, fname))
        rmdir(self.temp_dir)
        
    def test_build_entities_from_files_without_config(self):
        """
        Tests the ``build_entities_from_files`` method when no config
        file is specified.
        """
        filelist = [self.datapath("file1.xml"),
                    self.datapath("file2.xml"),
                    self.datapath("file3.xml")]
        result = self.controller.build_entities_from_files(filelist)
        self.assertEqual(result,
            [("Read from %s with None config" % self.datapath("file1.xml"),
              self.datapath("file1")),
             ("Read from %s with None config" % self.datapath("file2.xml"),
              self.datapath("file2")),
             ("Read from %s with None config" % self.datapath("file3.xml"),
              self.datapath("file3")),
            ])

    def test_build_entities_from_files_with_config(self):
        """
        Tests the ``build_entities_from_files`` method when a config
        file is specified.
        """
        filelist = [self.datapath("file1.xml"),
                    self.datapath("file2.xml"),
                    self.datapath("file3.xml")]
        cfgfile = self.datapath("config.xml")
        result = self.controller.build_entities_from_files(filelist,
                                                           cfgfile)
        self.assertEqual(result,
            [("Read from %s with %s config" % (self.datapath("file1.xml"),
                                               self.datapath("config.xml")),
              self.datapath("file1")),
             ("Read from %s with %s config" % (self.datapath("file2.xml"),
                                               self.datapath("config.xml")),
              self.datapath("file2")),
             ("Read from %s with %s config" % (self.datapath("file3.xml"),
                                               self.datapath("config.xml")),
              self.datapath("file3")),
            ])

    def test_write_pdf_to_files(self):
        """
        Tests the ``write_pdf_to_files`` method.
        """ 
        entitylist = [("entity1", "file1.pdf"),
                      ("entity2", "file2.pdf"),
                      ("entity3", "file3.pdf")]
        self.controller.write_pdf_to_files(entitylist)
        result = self.controller.pdf_writer.writes
        self.assertEqual(result,
                          ["PDF write from entity1 in file1.pdf",
                           "PDF write from entity2 in file2.pdf",
                           "PDF write from entity3 in file3.pdf"])

    def test_save_entities_to_xml_files(self):
        """
        Tests the ``save_entities_to_files`` method.
        """
        # Prepares the test
        for fname in listdir(self.datapath("accounting_dir")):
            copy(self.datapath("accounting_dir/%s" % fname),
                 osp.join(self.temp_dir, fname))
        # Does the actual test
        entitylist = [(Bill("id0"), osp.join(self.temp_dir, "accdoc0.xml")),
                      (Bill("id1"), osp.join(self.temp_dir, "accdoc1.xml")),
                      (Bill("id2"), osp.join(self.temp_dir, "accdoc2.xml")),
                      (Bill("id3"), osp.join(self.temp_dir, "accdoc3.xml"))]
        self.controller.save_entities_to_files(entitylist, ENCODING)
        files = listdir(self.temp_dir)
        files.sort()
        self.assertEqual(files, ["accdoc0.xml", "accdoc1.xml",
                                  "accdoc1.xml.old", "accdoc2.xml",
                                  "accdoc2.xml.old", "accdoc3.xml"])
        for filename, exp_id in [("accdoc0.xml", u"id0"),
                                 ("accdoc1.xml", u"id1"),
                                 ("accdoc1.xml.old", u"id1-prev"),
                                 ("accdoc2.xml", u"id2"),
                                 ("accdoc2.xml.old", u"id2-prev"),
                                 ("accdoc3.xml", u"id3")]:
            root = etree.parse(osp.join(self.temp_dir, filename)).getroot()
            doc_id = root.findtext(u"{%s}metadata/{%s}id"
                                                 % (PBD_XMLNS, PBD_XMLNS), u"")
            self.assertEqual(doc_id, exp_id)
        
    def test_export_accounting_entries_to_xml_file(self):
        """
        Tests the ``export_accounting_entries_to_xml_file`` method.
        """ 
        entitylist = ["entity1", "entity2", "entity3"]
        self.controller.export_accounting_entries_to_xml_file(entitylist,
                                                         "fileA.xml", ENCODING)
        result = self.controller.entries_generator.actions
        self.assertEqual(result,
                    ["Deletes all entries",
                     "Generates accounting entry for entity1",
                     "Generates accounting entry for entity2",
                     "Generates accounting entry for entity3",
                     "Writes entries in fileA.xml XML file in UTF-8 encoding"])


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()


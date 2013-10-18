import doc
import unittest
import data_for_testing

class DocTestCases(unittest.TestCase):
    def testsimple(self):
        d = doc.Doc(data_for_testing.simple_xml_file_obj())
        self.assertEquals(d.guidata.skin.scoreFontName, "Tahoma Bold")




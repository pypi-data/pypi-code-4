import unittest
import StringIO
import read_config
import doc
import data_for_testing

"""
./read_config.py  gui.xml guidata.skin.scoreFontName
'GUIDATA_SKIN_SCOREFONTNAME="Tahoma Bold"
"""

class ReadConfigTestCase(unittest.TestCase):
    def test_make_name(self):
        actual_name = read_config.make_enviroment_name("guidata.skin.scoreFontName")
        self.assertEquals("GUIDATA_SKIN_SCOREFONTNAME", actual_name)
        

    def test_line(self):
        d = doc.Doc(data_for_testing.simple_xml_file_obj())
        actual_line = read_config.make_line(d, "guidata.skin.scoreFontHeight")
        self.assertEquals("export GUIDATA_SKIN_SCOREFONTHEIGHT=20", actual_line)

    def test_line_with_space(self):
        d = doc.Doc(data_for_testing.simple_xml_file_obj())
        actual_line = read_config.make_line(d, "guidata.skin.scoreFontName")
        self.assertEquals('export GUIDATA_SKIN_SCOREFONTNAME=Tahoma_Bold', actual_line)


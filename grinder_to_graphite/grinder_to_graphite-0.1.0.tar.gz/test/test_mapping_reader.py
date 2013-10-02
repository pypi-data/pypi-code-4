import unittest
from g2g import g2g_config
from g2g.logtype.grinder.mapping_reader import MapReader
import os

_ROOT_DIR = os.getcwd()
if _ROOT_DIR.endswith("test"):
    _ROOT_DIR = _ROOT_DIR[:len(_ROOT_DIR) - 5]
HTTP_MAPPING_FILE = "%s/test/data/http.mapping" % _ROOT_DIR
INCOMPLETE_MAPPING_FILE = "%s/test/data/incomplete.http.mapping" % _ROOT_DIR


class TestMapReader(unittest.TestCase):

    def setUp(self):
        self.configfile = "config.delete.me"
        g2g_config.create_example_config_file(self.configfile)
        self.config = g2g_config.get_config([self.configfile])

    def tearDown(self):
        if os.path.exists(self.configfile):
            os.remove(self.configfile)

    def test_get_tx_names_happypath(self):
        map_reader = MapReader()
        tx_names = map_reader.get_tx_names(HTTP_MAPPING_FILE)
        self.assertGreater(len(tx_names), 1)

    def test_get_tx_names_no_mapping_file(self):
        map_reader = MapReader()
        with self.assertRaises(SystemExit) as cm:
            map_reader.get_tx_names("missing.file")
        self.assertEqual(cm.exception.code, 1)

    def test_get_tx_names_incomplete_mapping_file(self):
        map_reader = MapReader()
        with self.assertRaises(SystemExit) as cm:
            map_reader.get_tx_names(INCOMPLETE_MAPPING_FILE)
        self.assertEqual(cm.exception.code, 1)

    def test_get_duplicates(self):
        original_list = [1, 2, 3, 4, 4, 5, 5, 5]
        map_reader = MapReader()
        new_list = map_reader._get_duplicates(original_list)
        self.assertEqual([4, 5], new_list)

import unittest
from glf import engine, glf_config
from glf.logtype.grinder.data_reader import LineReader as GrinderLineReader
from glf import config_param
from os.path import expanduser
import os

HOME = expanduser("~")
HTTP_DATA_FILE="test/data/example_http.mapping"

class TestEngine(unittest.TestCase):

    def setUp(self):
        pass
    
    def _create_tmp_file(self, file_name):
        if os.path.exists(file_name):
            return
        f = open(file_name, "w")
        f.write(".")
        f.close()
        
    def _delete_tmp_file(self, file_name):
        if os.path.exists(file_name):
            os.remove(file_name)

    def test_get_offset_file(self):
        # missing data file
        of = engine._get_offset_file("/etc/hosts.fake")
        self.assertIsNone(of)
        
        # data file is relative path in current dir
        data_file = "delete.me"
        self._create_tmp_file(data_file)
        of = engine._get_offset_file(data_file)
        self.assertEqual(of, glf_config.DOTDIR + os.sep + data_file + ".offset")
        self._delete_tmp_file(data_file)
        
        # data file is relative path in current dir
        root_dir = "deleteme"
        filename = "xyz"
        os.mkdir(root_dir)
        data_file = root_dir + os.sep + filename
        self._create_tmp_file(data_file)
        of = engine._get_offset_file(data_file)
        self.assertEqual(of, glf_config.DOTDIR + os.sep + root_dir + "." + filename + ".offset")
        self._delete_tmp_file(data_file)  
        os.rmdir(root_dir)
         
        # data file is absolute path
        data_file = "/etc/hosts"
        self._create_tmp_file(data_file)
        of = engine._get_offset_file(data_file)
        self.assertEqual(of, glf_config.DOTDIR + os.sep + "etc.hosts.offset")


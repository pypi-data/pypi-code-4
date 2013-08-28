# coding: utf-8
import unittest

from nose.tools import raises

from gat_runner.languages import *


class GATFileTests(unittest.TestCase):
    def test_get_file_name_and_extensions(self):
        self.assertEquals(('file', 'py'), GATFileFactory.get_filename_and_extension('file.py'))
        self.assertEquals(('file.x', 'py'), GATFileFactory.get_filename_and_extension('file.x.py'))
        self.assertEquals(('file', 'py'), GATFileFactory.get_filename_and_extension('/usr/x/file.py'))

    @raises(ValueError)
    def test_not_supported_language(self):
        GATFileFactory.create('file.invalid_language')

    def test_valid_language(self):
        gatfile = GATFileFactory.create('file.py')
        self.assertEquals(['python', 'file.py'], gatfile.get_runtime_command())


class JavaFileTests(unittest.TestCase):
    def test_main_class_in_the_current_dit(self):
        java = GATFileFactory.create('Class.java')
        main_class = java.get_runtime_command()[3]
        self.assertEquals('Class', main_class)

    def test_main_class_in_a_subdir(self):
        java = GATFileFactory.create('./dir/Class.java')
        main_class = java.get_runtime_command()[3]
        self.assertEquals('Class', main_class)

    def test_main_class_in_a_subdir2(self):
        java = GATFileFactory.create('dir/Class.java')
        main_class = java.get_runtime_command()[3]
        self.assertEquals('Class', main_class)

    def test_main_class_in_a_root_dir(self):
        java = GATFileFactory.create('/dir/Class.java')
        main_class = java.get_runtime_command()[3]
        self.assertEquals('Class', main_class)


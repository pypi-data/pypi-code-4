# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main
from os import path as osp

from pybill.lib.config.register import ConfigRegister


TEST_DATA_DIR = unicode(osp.join(osp.dirname(osp.abspath(__file__)), u"data"))


class TestableConfigRegister(ConfigRegister):
    """
    Class only defined for test purposes. Redefines the class
    constants in order to be able to do the tests.
    """
    SYSTEM_CONFIG_DIR = osp.join(TEST_DATA_DIR, u"system_dir")
    USER_CONFIG_DIR = osp.join(TEST_DATA_DIR, u"user_dir")
    DEFAULT_CONFIG_REF = u"default" 

class TestableConfigRegister2(ConfigRegister):
    """
    Class only defined for test purposes. Redefines the class
    constants in order to be able to do the tests.
    """
    SYSTEM_CONFIG_DIR = osp.join(TEST_DATA_DIR, u"system_dir")
    USER_CONFIG_DIR = osp.join(TEST_DATA_DIR, u"user_dir")
    DEFAULT_CONFIG_REF = u"non-existing-default" 


class ConfigRegisterTest(TestCase) :
    def setUp(self) :
        """
        Called before each test from this class
        """
        self.register = TestableConfigRegister()

    def test_real_class_constants(self):
        """
        Tests the value of the class constants in the real register class.
        """
        real_reg = ConfigRegister()
        self.assertEqual(real_reg.__class__.SYSTEM_CONFIG_DIR,
                          u"/etc/pybill/config/")
        self.assertEqual(real_reg.__class__.USER_CONFIG_DIR,
                          u"~/.config/pybill/")
        self.assertEqual(real_reg.__class__.DEFAULT_CONFIG_REF,
                          u"default")

    def test_find_file_defined_in_first_dir(self):
        """
        Tests the find_config_file method for a file that only exists in the
        user directory.
        """
        filename = self.register.find_config_file(u"config2")
        self.assertEqual(filename,
                          unicode(self.datapath(u"user_dir/config2.xml")))
        
    def test_find_file_defined_in_second_dir(self):
        """
        Tests the find_config_file method for a file that only exists in the
        system directory.
        """
        filename = self.register.find_config_file(u"config1")
        self.assertEqual(filename,
                          unicode(self.datapath(u"system_dir/config1.xml")))
        
    def test_find_file_defined_in_both_dirs(self):
        """
        Tests the find_config_file method for a file that exists in the user
        directory and the system directory.
        """
        filename = self.register.find_config_file(u"default")
        self.assertEqual(filename,
                          unicode(self.datapath(u"user_dir/default.xml")))

    def test_find_default_file(self):
        """
        Tests the find_config_file method for the file that contains the
        default configuration.
        """
        filename = self.register.find_config_file(
                                   self.register.__class__.DEFAULT_CONFIG_REF)
        self.assertEqual(filename,
                          unicode(self.datapath(u"user_dir/default.xml")))

    def test_find_file_from_filepath(self):
        """
        Tests the find_config_file method for a file defined by its file path.
        """
        filename = self.register.find_config_file(
                                unicode(self.datapath("user_dir/config2.xml")))
        self.assertEqual(filename,
                          unicode(self.datapath(u"user_dir/config2.xml")))

    def test_store_config(self):
        """
        Tests the store_config method.
        """
        self.register.store_config(u"DEFAULT2",
                             unicode(self.datapath(u"system_dir/default.xml")))
        self.assertTrue(u"DEFAULT2" in self.register.configs)
        cfg = self.register.configs[u"DEFAULT2"]
        self.assertEqual(cfg.reference, u"DEFAULT2")
        self.assertEqual(cfg.company_logo, u"B1")
        self.assertEqual(cfg.company_address.name, u"B2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"B3")

    def test_store_config_from_filepath(self):
        """
        Tests the store_config method with a configuration defined by its
        filepath.
        """
        filepath = unicode(self.datapath(u"system_dir/config1.xml"))
        self.register.store_config(filepath, filepath)
        self.assertTrue(filepath in self.register.configs)
        cfg = self.register.configs[filepath]
        self.assertEqual(cfg.reference, filepath)
        self.assertEqual(cfg.company_logo, u"C1")
        self.assertEqual(cfg.company_address.name, u"C2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"C3")

    def test_initialisation(self):
        """
        Tests the register was correctly initialized and has read the default
        configuration.
        """
        self.assertEqual(self.register.configs.keys(), [u"default"])
        cfg = self.register.configs[u"default"]
        self.assertEqual(cfg.reference, u"default")
        self.assertEqual(cfg.company_logo, u"A1")
        self.assertEqual(cfg.company_address.name, u"A2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"A3")

    def test_initialisation_with_non_existing_default(self):
        """
        Tests the register is correctly initialized when the default
        configuration doesn't exist (the default configuration is then an
        empty configuration object).
        """
        other_reg = TestableConfigRegister2()
        self.assertEqual(other_reg.configs.keys(), [u"non-existing-default"])
        cfg = other_reg.configs[u"non-existing-default"]
        self.assertEqual(cfg.reference, None)
        self.assertEqual(cfg.company_logo, u"")
        self.assertEqual(cfg.company_address.name, u"")
        self.assertEqual(cfg.local_phrases, {})

    def test_get_read_config(self):
        """
        Tests the get_config method for an already read configuration.
        """
        self.register.store_config(u"config1",
                             unicode(self.datapath(u"system_dir/config1.xml")))
        cfg = self.register.get_config(u"config1")
        self.assertEqual(cfg.reference, u"config1")
        self.assertEqual(cfg.company_logo, u"C1")
        self.assertEqual(cfg.company_address.name, u"C2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"C3")

    def test_get_non_read_config(self):
        """
        Tests the get_config method for a configuration that wasn't previously
        read.
        """
        self.register.store_config(u"config1",
                             unicode(self.datapath(u"system_dir/config1.xml")))
        cfg = self.register.get_config(u"config2")
        self.assertEqual(cfg.reference, u"config2")
        self.assertEqual(cfg.company_logo, u"D1")
        self.assertEqual(cfg.company_address.name, u"D2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"D3")
        # Checks the newly-read configuration has been added in the register
        self.assertTrue(u"config2" in self.register.configs)
        cfg = self.register.configs[u"config2"]
        self.assertEqual(cfg.reference, u"config2")
        self.assertEqual(cfg.company_logo, u"D1")
        self.assertEqual(cfg.company_address.name, u"D2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"D3")

    def test_get_non_existing_config(self):
        """
        Tests the get_config method for a configuration that doesn't exist (the
        method returns the default configuration).
        """
        self.register.store_config(u"config1",
                             unicode(self.datapath(u"system_dir/config1.xml")))
        cfg = self.register.get_config(u"config3")
        self.assertEqual(cfg.reference, u"default")
        self.assertEqual(cfg.company_logo, u"A1")
        self.assertEqual(cfg.company_address.name, u"A2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"A3")
        # Checks the non existing configuration wasn't added in the register
        self.assertFalse(u"config3" in self.register.configs)

    def test_get_read_config_doesn_t_read_from_disk(self):
        """
        Tests the get_config method for an already read configuration doesn't
        read the configuration from the disk
        """
        self.register.store_config(u"config1",
                             unicode(self.datapath(u"system_dir/config1.xml")))
        self.register.configs[u"default"].company_logo = u"F45"
        cfg = self.register.get_config(u"default")
        self.assertEqual(cfg.reference, u"default")
        self.assertEqual(cfg.company_logo, u"F45")
        self.assertEqual(cfg.company_address.name, u"A2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"A3")

    def test_get_config_from_filepath(self):
        """
        Tests the get_config method for a configuration defined by its filepath.
        """
        filepath = unicode(self.datapath(u"system_dir/config1.xml"))
        cfg = self.register.get_config(filepath)
        self.assertEqual(cfg.reference, filepath)
        self.assertEqual(cfg.company_logo, u"C1")
        self.assertEqual(cfg.company_address.name, u"C2")
        self.assertEqual(cfg.local_phrases[u"bill"], u"C3")
        self.assertTrue(filepath in self.register.configs)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()

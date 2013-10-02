import unittest
import os
from g2g import g2g_config
import yaml

class TestConfig(unittest.TestCase):
    
    def setUp(self):
        self.dotfilename = "dot.delete.me"
        self.dotfile = "%s/%s" % (g2g_config.DOTDIR, self.dotfilename)
        self.configfile = "config.delete.me"
        
    def tearDown(self):
        if os.path.exists(self.dotfile):
            os.remove(self.dotfile)
        if os.path.exists(self.configfile):
            os.remove(self.configfile)
        
    def test_create_new_dotfile(self):
        self.assertFalse(os.path.exists(self.dotfile))
        g2g_config.set_default_config(self.configfile, dotfile=self.dotfilename)
        self.assertTrue(os.path.exists(self.dotfile), "dot file %s not created" % self.dotfile)
        conf = open(self.dotfile).read()
        self.assertEqual(conf, self.configfile)
    
    def test_overwrite_existing_dotfile(self):
        initial_config_file = "random contents"
        g2g_config.set_default_config(initial_config_file, dotfile=self.dotfilename)
        g2g_config.set_default_config(self.configfile, dotfile=self.dotfilename)
        conf = open(self.dotfile).read()
        self.assertEqual(conf, self.configfile)
        
    def test_write_example_file(self):
        self.assertFalse(os.path.exists(self.configfile))
        g2g_config.create_example_config_file(self.configfile)
        self.assertTrue(os.path.exists(self.configfile))
        config = g2g_config.G2GConfiguration(self.configfile)
        self.assertEqual(config.carbon_port, 2003)

    def test_load_specified_config(self):
        g2g_config.create_example_config_file(self.configfile)
        config = g2g_config.get_config([self.configfile])
        self.assertNotEqual(None, config)
        self.assertEqual(config.carbon_port, 2003)
       
    def test_load_default_config_no_default(self):
        self.assertFalse(os.path.exists(self.dotfile))
        config = g2g_config.get_config([], dotfilename=self.dotfile)
        self.assertEqual(None, config)
    
    def test_load_default_config_with_default(self):
        self.assertFalse(os.path.exists(self.dotfile))
        self.assertFalse(os.path.exists(self.configfile))
        g2g_config.create_example_config_file(self.configfile)
        self.assertTrue(os.path.exists(self.configfile))
        g2g_config.set_default_config(self.configfile, dotfile=self.dotfilename)
        self.assertTrue(os.path.exists(self.dotfile))
        config = g2g_config.get_config([], dotfilename=self.dotfilename)
        
    def test_missing_analysis_section(self):
        g2g_config.create_example_config_file(self.configfile)
        yaml_data = yaml.load(open(self.configfile), Loader=yaml.Loader)
        del(yaml_data["g2g"]["analysis"])
        config = g2g_config.G2GConfiguration(None, yaml_data)
        self.assertEqual(config.time_group_ms, [])
        self.assertEqual(config.response_time_percentiles, [])

    def test_default_analysis_section(self):
        g2g_config.create_example_config_file(self.configfile)
        config = g2g_config.get_config([self.configfile])
        self.assertEqual(config.time_group_ms, [100,200])
        self.assertEqual(config.response_time_percentiles, [0.5, 0.95, 0.99])
        
    def test_missing_run_section(self):
        g2g_config.create_example_config_file(self.configfile)
        yaml_data = yaml.load(open(self.configfile), Loader=yaml.Loader)
        del(yaml_data["g2g"]["run"])
        config = g2g_config.G2GConfiguration(None, yaml_data)
        self.assertFalse(config.follow)
        self.assertEqual(config.follow_interval_seconds, 60)
        self.assertFalse(config.resume)
        
    def test_default_run_section(self):
        g2g_config.create_example_config_file(self.configfile)
        config = g2g_config.get_config([self.configfile])
        self.assertFalse(config.follow)
        self.assertEqual(config.follow_interval_seconds, 60)
        self.assertFalse(config.resume)
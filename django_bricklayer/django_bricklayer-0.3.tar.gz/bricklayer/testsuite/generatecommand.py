from django.test import TestCase
from bricklayer.utils import *
import test_app
import os, imp

class GenerateCommandTestCase(TestCase):
    
    def setUp(self):
        
        self.app_path = os.path.abspath(test_app.__path__[0])
        run_manage_py("generatecommand test_command test_app")
    
    def tearDown(self):
        try:
            os.remove( os.path.join(self.app_path, "management","commands","__init__.py") )
            os.remove( os.path.join(self.app_path, "management","commands","test_command.py") )
            os.remove( os.path.join(self.app_path, "management","__init__.py") )
            os.rmdir( os.path.join(self.app_path, "management","commands") )
            os.rmdir( os.path.join(self.app_path, "management" ) )
        except: pass
    
    def test_commands(self):
        msg = ''
        # Folder creation
        self.assertTrue(exists_path( self.app_path,"management"), msg)
        self.assertTrue(os.path.isdir(os.path.join(self.app_path,"management")),msg)
        self.assertTrue(exists_path(self.app_path,"management","commands"),msg)
        self.assertTrue(os.path.isdir(os.path.join(self.app_path,"management","commands")),msg)
        # Check that are valid python packages
        self.assertTrue(exists_path(self.app_path,"management", "__init__.py"),msg)
        self.assertTrue(exists_path(self.app_path,"management","commands","__init__.py"),msg)
        self.assertTrue(exists_path(self.app_path,"management","commands","test_command.py"),msg)
    
    def test_shortcut_creation(self):
        command_module = imp.load_source('commands', os.path.join(self.app_path, 'management', 'commands', '__init__.py'))
        self.assertIn('TestCommandCommand', dir(command_module))

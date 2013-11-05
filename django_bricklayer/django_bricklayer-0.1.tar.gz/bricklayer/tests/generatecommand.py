from django.test import TestCase
from bricklayer.utils import *
import test_app
import os
class CreateCommandTestCase(TestCase):
    
    def setUp(self):
        
        self.app_path = os.path.abspath(test_app.__path__[0])
    
    def tearDown(self):
        try:
            os.remove( os.path.join(self.app_path, "management","commands","__init__.py") )
            os.remove( os.path.join(self.app_path, "management","commands","test.py") )
            os.remove( os.path.join(self.app_path, "management","__init__.py") )
            os.rmdir( os.path.join(self.app_path, "management","commands") )
            os.rmdir( os.path.join(self.app_path, "management" ) )
        except: pass
    
    def makeAssertions(self, msg=""):
        # Folder creation
        self.assertTrue(exists_path( self.app_path,"management"), msg)
        self.assertTrue(os.path.isdir(os.path.join(self.app_path,"management")),msg)
        self.assertTrue(exists_path(self.app_path,"management","commands"),msg)
        self.assertTrue(os.path.isdir(os.path.join(self.app_path,"management","commands")),msg)
        # Check that are valid python packages
        self.assertTrue(exists_path(self.app_path,"management", "__init__.py"),msg)
        self.assertTrue(exists_path(self.app_path,"management","commands","__init__.py"),msg)
        self.assertTrue(exists_path(self.app_path,"management","commands","test.py"),msg)
        
    def test_commands(self):
        """
            Check creation of "management" and "management.command" packages 
            using different args variations
        """
        args_combinations =( 
                            ("test","test_app"),
                            ("test", "-4", "test_app"),
                            ("test", "--for", "test_app"),
                            ("-c","test","test_app"),
                            ("--cmd","test","test_app"),
                            ("-c","test", "-4", "test_app"),
                            ("--cmd","test", "-4", "test_app"),
                            ("-c","test", "--for", "test_app"),
                            ("--cmd","test", "--for", "test_app"),
                            )
       
        
        
        for args_set in args_combinations:
            run_manage_py("generatecommand "+ " ".join(args_set))
            error_msg = "Fail using %s"%str(args_set)
            self.makeAssertions(error_msg)
            self.tearDown()
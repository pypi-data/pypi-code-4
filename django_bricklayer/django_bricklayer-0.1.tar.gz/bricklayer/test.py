from django.test import TestCase, LiveServerTestCase
from django.core import management
from django.utils.module_loading import import_module, import_by_path 
import test_app
import os
from selenium import webdriver
from bricklayer.utils import run_manage_py, exists_path, exists_dir
from django.db import models
from django.core.urlresolvers import resolve, reverse_lazy, reverse
SAMPLE_ADMIN_FILE = """
from django.contrib import admin
from test_app.models import TestModel

class TestModelAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(TestModel, TestModelAdmin)
"""


        
        

        
class CreateAdminCommandTest(LiveServerTestCase):
    fixtures = ['admin_user.json']
    
    def setUp(self):
        self.app_path = os.path.abspath(test_app.__path__[0])
        self.admin_py_path = os.path.join( self.app_path, "admin.py")
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)
        
    def runCommandAndCheckAdminSite(self):
        management.call_command("createadmin", "test_app")
        self.assertTrue(os.path.exists(self.admin_py_path))
        
        # navigate to admin page and check modules have been added
        self.browser.get(self.live_server_url +  '/admin/')
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys('luca')
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('test')
        self.browser.find_element_by_xpath('//input[@value="Log in"]').click()
        body = self.browser.find_element_by_tag_name("body")
        
        self.assertIn('test models', body.text.lower())
        self.assertIn('another test models', body.text.lower())
        
    def test_create_admin_for_all_model_in_app(self):
        """
        Test admin file creation for each model in the app
        """
       
        # navigate to admin page and check modules have been added
        self.runCommandAndCheckAdminSite()
        self.removeAdminFile()
    
    def test_createadmin_when_empty_admin_py_already_exists(self):
        """
            Test manage.py createadmin APPNAME when an empty admin.py already exists
        """
        
        
        with open(self.admin_py_path,'w') as admin_file:
            admin_file.write("")
        self.runCommandAndCheckAdminSite()
        self.removeAdminFile()
        
    def test_createadmin_when_not_empty_admin_py_already_exists(self):
        """
            Test manage.py createadmin ALL when an admin.py file for
            that app already exists.
        """
        
        with open(self.admin_py_path,'w') as admin_file:
            admin_file.write(SAMPLE_ADMIN_FILE)
        
        self.runCommandAndCheckAdminSite()
        
        self.removeAdminFile()
    
    def removeAdminFile(self):
        os.remove(self.admin_py_path)
        
    def tearDown(self):
        self.browser.quit()
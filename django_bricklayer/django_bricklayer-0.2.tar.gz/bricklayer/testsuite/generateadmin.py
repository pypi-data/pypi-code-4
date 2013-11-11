from django.test import TestCase
from bricklayer.utils import run_manage_py, exists_path
import test_app, os

class GenerateAdminTestCase(TestCase):
	def setUp(self):
		self.app_path = os.path.abspath(test_app.__path__[0])
		run_manage_py("generateadmin test_app")
		
	def test_admin_py_exists(self):
		self.assertTrue(exists_path(self.app_path, 'admin.py'))

	def test_admin_py_code(self):
		with open(os.path.join(self.app_path, 'admin.py')) as f:
			source_code = "".join(f.readlines())
		#check imports
		self.assertIn("from django.contrib import admin", source_code)
		self.assertIn("from test_app.models import TestModel", source_code)
		self.assertIn("admin.site.register(TestModel, TestModelAdmin)", source_code)
		self.assertIn("class TestModelAdmin(admin.ModelAdmin):", source_code)




	def tearDown(self):
		os.remove(os.path.join(self.app_path, 'admin.py'))
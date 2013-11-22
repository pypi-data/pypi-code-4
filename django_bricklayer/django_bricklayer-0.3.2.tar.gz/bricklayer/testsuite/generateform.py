from django.test import TestCase
from bricklayer.utils import run_manage_py, exists_path
import test_app, os, imp

class GenerateFormTestCase(TestCase):

	def setUp(self):
		self.app_path = os.path.abspath(test_app.__path__[0])
		run_manage_py("generateform test_app -m TestModel")

	def test_file_creation(self):
		self.assertTrue(exists_path(self.app_path, "forms.py"))


	def test_form(self):
		forms = dir(imp.load_source('forms', os.path.join(self.app_path, "forms.py") ) )
		self.assertIn("TestModelForm", forms)
	

	def tearDown(self):
		os.remove(os.path.join(self.app_path, "forms.py"))

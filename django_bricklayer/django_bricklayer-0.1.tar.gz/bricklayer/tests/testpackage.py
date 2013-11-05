from django.test import TestCase
from bricklayer.utils import *
import test_app, os, imp


class TestFolderTestCase(TestCase):
	def setUp(self):
		self.app_path = os.path.abspath(test_app.__path__[0])
		with open(os.path.join(self.app_path, "tests.py")) as f:
			self.tests_content = "".join(f.readlines())
		run_manage_py("testpackage test_app")

	def test_folder(self):
		"""
			Test folder structure
		"""
		self.assertTrue(exists_dir(self.app_path, "tests"))
		self.assertTrue(exists_path(self.app_path, "tests","__init__.py"))
		self.assertTrue(exists_path(self.app_path, "tests","test_app.py"))
		# Old tests.py file is removed to avoid confilcts
		self.assertFalse(exists_path(self.app_path, "tests.py"))

	def test_test_module(self):
		with open(os.path.join(self.app_path, 'tests', '__init__.py')) as f:
			test_text = f.read()

		self.assertIn("__test__= {}", test_text)

	def tearDown(self):
		self.app_path = os.path.abspath(test_app.__path__[0])
		with open(os.path.join(self.app_path, "tests.py"),"w") as f:
			f.write(self.tests_content)

		for file in os.listdir(os.path.join(self.app_path, "tests" )):
			os.remove(os.path.join(self.app_path, "tests", file))

		os.rmdir(os.path.join(self.app_path, "tests" ))
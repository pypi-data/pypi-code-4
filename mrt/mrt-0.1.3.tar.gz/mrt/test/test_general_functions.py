#!/usr/bin/python


import unittest

from general_functions import *

class GeneralFunctionsTest(unittest.TestCase):
   def testFileDoesNotExist(self):
      self.assertRaises(Exception, check_if_file_exists, "non_existing_file.txt")

   def testDirDoesNotExist(self):
      self.assertRaises(Exception, check_if_dir_exists, "non_existing_dir")

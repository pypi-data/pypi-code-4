#!/usr/bin/python

import unittest

from args import *

class ArgsTest(unittest.TestCase):
   def testArgsNoInputFile(self):
      my_args = {
            'input_file_name'     : None,
            'output_dir_name'     : "my_output_dir",
            'run_all'             : True,
            'extract_code_blocks' : False,
            'execute_code_blocks' : False,
            'generate_report'     : False
            }
      self.assertRaises(ArgsException, validate_command_line_arguments, my_args)

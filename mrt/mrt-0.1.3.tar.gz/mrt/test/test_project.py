#!/usr/bin/python

import os
import shutil
import unittest

from project import *

class ProjectTest(unittest.TestCase):
   def setUp(self):
      # standard file names for these tests:
      self.input_file = "test_input_file.mrt"
      self.output_dir = "test_output"

      # create an input file
      open('./{0}'.format(self.input_file),'w').write(""""<h1>Just a test</h1>

This is some text...
<<env=shell, title=my_title>>=
ls
@
""")

   def tearDown(self):
      os.remove(self.input_file)
      # remove output directory if it exists
      if os.path.exists(self.output_dir):
         shutil.rmtree(self.output_dir)

   def testIndexFile(self):
      x = Project(self.input_file, self.output_dir)
      self.assertEquals(x.get_output_index_file(), "test_output/index.html")

   def testCorpusFile(self):
      x = Project(self.input_file, self.output_dir)
      self.assertEquals(x.get_output_corpus_file(), "test_output/corpus.html")

   def testProjectFile(self):
      x = Project(self.input_file, self.output_dir)
      self.assertEquals(x.get_project_file(), "test_output/project.pk")

   def testHtmlAfterExtractCodeBlocks(self):
      x = Project(self.input_file, self.output_dir)
      x.extract_blocks()
      assert("<h1>" in x.html_corpus[0])

   def testNumberOfBlocksAfterExtractCodeBlocks(self):
      x = Project(self.input_file, self.output_dir)
      x.extract_blocks()
      self.assertEquals(len(x.blocks), 1)

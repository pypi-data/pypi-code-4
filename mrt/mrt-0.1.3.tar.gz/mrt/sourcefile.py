#!/usr/bin/python

import os
import sys

from sourcefileline import *
from block import *
from general_functions import *






class SourceFile(object):
   """
   An instance of this class represents a complete input file
   containing code blocks for several environments.

   This object is constructed as a list of individual lines,
   represented by the SourceFileLine class.
   """
   def __init__(self, file_name):
      exit_if_file_does_not_exist(file_name)
      self.file_name = file_name
      self.lines     = self.__read_source_file()

      self.__validate_code_blocks_structure()






   def render_blocks_from_source_file(self):
      """
      Goes through each line of the input file and generates
      individual mothur/shell scripts and a main output documentation
      file in HTML.

      Returns a list of Block objects.

      TODO: the hash-bang should be configurable by the user
      """
      docfile    = []  # a list of lines
      all_blocks = []  # a list of instances of class Block

      for this_line in self.lines:
         # The environment of the current line is one of:
         # - doc
         # - begin_shell
         # - begin_mothur
         # - end
         # - shell
         # - mothur
         #
         # Each of these implies a specific action.
         if this_line.environment == "doc":
            docfile.append(this_line.text)
            next
         
         if this_line.environment == "begin_shell":
            current_block = CodeBlock(
                  block_title     = this_line.name,
                  environment     = "shell",
                  as_html         = this_line.as_html,
                  collapse_script = this_line.collapse_script,
                  collapse_stdout = this_line.collapse_stdout,
                  collapse_stderr = this_line.collapse_stderr
                  )
            current_block.lines.append("#!/bin/bash\n\n")
            next

         if this_line.environment == "begin_mothur":
            current_block = CodeBlock(
                  block_title     = this_line.name,
                  environment     = "mothur",
                  as_html         = this_line.as_html,
                  collapse_script = this_line.collapse_script,
                  collapse_stdout = this_line.collapse_stdout,
                  collapse_stderr = this_line.collapse_stderr
                  )
            current_block.lines.append("#!/usr/bin/env mothur\n\n")
            next

         if this_line.environment == "end":
            all_blocks.append(current_block)
            docfile.append("<!-- below: results from file {0} -->\n".format(current_block.file_name_script))
            docfile.append("<!-- above: results from file {0} -->\n".format(current_block.file_name_script))
            #result.append(current_block)
            next

         if this_line.environment == "shell":
            current_block.lines.append(this_line.text)
            next

         if this_line.environment == "mothur":
            current_block.lines.append(this_line.text)
            next

         if this_line.environment == "insert_fig":
            current_block = SingleLineBlock(
                  environment     = "insert_fig",
                  img             = this_line.img,
                  label           = this_line.label
            )
            docfile.append("<!-- below: insert_fig {0} -->\n".format(current_block.random_number))
            docfile.append("<!-- above: insert_fig {0} -->\n".format(current_block.random_number))
            all_blocks.append(current_block)
            next

         if this_line.environment == "insert_file":
            current_block = SingleLineBlock(
                  environment     = "insert_file",
                  data            = this_line.data,
                  label           = this_line.label
            )
            docfile.append("<!-- below: insert_file {0} -->\n".format(current_block.random_number))
            docfile.append("<!-- above: insert_file {0} -->\n".format(current_block.random_number))
            all_blocks.append(current_block)
            next

      return (docfile, all_blocks)






   def print_output(self):
      for this_line in self.lines:
         this_line.print_output()






   def __read_source_file(self):
      """
      Opens a file and extracts (and interprets) the lines in it.

      Returns a list of SourceFileLine instances.
      """
      try:
         raw_lines = list(open(self.file_name,"r"))
      except:
         sys.exit("I could not read file '{0}'".format(self.filename))

      result = [None] * len(raw_lines)
      for i, this_line in enumerate(raw_lines):
         result[i] = SourceFileLine(this_line, i+1)
      return result






   def __validate_code_blocks_structure(self):
      """
      Make sure the code blocks in the source file are constructed in a valid way:
      - each code block should have an end tag (@)
      - code blocks can not be nested
      """
      current_env = "doc"
      for this_line in self.lines:
         try:
            self.__isValidTransition(current_env, this_line)
            if this_line.environment == "NA":
               this_line.environment = current_env
            elif this_line.environment == "begin_shell":
               current_env = "shell"
            elif this_line.environment == "begin_mothur":
               current_env = "mothur"
            elif this_line.environment == "insert_fig":
               current_env = "doc"  # always return to "doc" as the ground state
            elif this_line.environment == "insert_file":
               current_env = "doc"  # always return to "doc" as the ground state
            elif this_line.environment == "end":
               current_env = "doc"  # always return to "doc" as the ground state
         except Exception,e:
            sys.exit(e)
      # at the end of the file, we should have closed the code blocks
      if current_env != "doc":
         sys.exit("Error: code block is not closed properly.  Please correct.")






   def __isValidTransition(self, current_env, new_line):
      """
      check if a transition from environments is valid.  For example:
      - you can not start a shell environment in a mothur environment
      - you can not put and end-tag (@) when no shell or mothur environment has been started

      TODO:
      each code block should have an end-tag (@)
      """
      isWrong = False
      # from shell code, you can only continue or end (not start mothur code)
      if current_env == "shell" and not ( new_line.environment == "NA" or new_line.environment == "end" ):
         isWrong = True
      # from mothur code, you can only continue or end (not start shell code)
      if current_env == "mothur" and not ( new_line.environment == "NA" or new_line.environment == "end" ):
         isWrong = True
      # from doc, you can only continue, begin shell or begin mothur code
      # (e.g., you can not put an "@"-line when no code block has started)
      if current_env == "doc" and not ( new_line.environment == "begin_shell"  or
                                        new_line.environment == "begin_mothur" or
                                        new_line.environment == "insert_fig"   or
                                        new_line.environment == "insert_file"  or
                                        new_line.environment == "NA"):
         isWrong = True
      # you should not have empty code blocks (i.e., begin-tag followed immediately by end-tag)
      # TODO: currently we can't detect code blocks with just empty lines inside them
      if ( current_env == "begin_shell" or current_env == "begin_mothur" ) and new_line.environment == "end":
         isWrong = True

      if isWrong:
         raise Exception("Error: invalid transition from '{0}' to '{1}' (line {2}).".format(current_env, new_line.environment, new_line.line_number))

#!/usr/bin/python

import re
import sys
import unittest



class SourceFileLine(object):
   """
   An instance of this class represents 1 line from a source file, including
   - the line itself as a stripped string
   - its environment:
         * HTML code ("doc")
         * Mothur code ("mothur")
         * shell code ("shell")
         * the beginning of a code block ("begin_mothur" or "begin_shell")
         * the end of a code block ("end")
   - its parameters (e.g., code block name)
   """
   pattern_begin_code_block = re.compile('^<<(.*)>>=$')
   pattern_end_code_block   = re.compile('^@$')
   pattern_special_command  = re.compile('^<<(.*)>>$')

   def __init__(self, text, line_number):
      self.line_number     = line_number
      self.text            = text
      self.stripped_text   = "NA"
      self.environment     = "NA"
      self.name            = "NA"
      self.as_html         = False
      self.img             = None
      self.data            = None
      self.label           = None
      self.collapse_script = False
      self.collapse_stdout = True
      self.collapse_stderr = True
      self.__strip_leading_and_trailing_chars()
      self.__recognize_block_begin_and_end()






   def __strip_leading_and_trailing_chars(self):
      """
      takes a string and removes leading and
      trailing spaces, tabs and newlines
      """
      self.stripped_text = self.text.strip(" \t\n")






   def __recognize_block_begin_and_end(self):
      """
      (1) tests if this string means the beginning
          of a code block (<<...>>=) or the end
          of a code block (@)
          or a single-line command (<<..>>)
      (2) reads the parameters of the header of this block
          (e.g., the environment: shell or Mothur)

      TODO: reading the parameters of block headers can be improved a lot
      """
      if self.stripped_text != None:  # otherwise the regex search returns an error
         if self.pattern_begin_code_block.match(self.stripped_text):
            arguments_string = self.pattern_begin_code_block.sub(r'\1', self.stripped_text)
            this_env, this_title, this_as_html, this_collapse_script, this_collapse_stdout, this_collapse_stderr = self.__read_arguments_from_block_header(arguments_string)

            self.environment     = "begin_{0}".format(this_env)
            self.name            = this_title
            self.as_html         = this_as_html
            self.collapse_script = this_collapse_script
            self.collapse_stdout = this_collapse_stdout
            self.collapse_stderr = this_collapse_stderr 

         elif self.pattern_end_code_block.match(self.stripped_text):
            self.environment = "end"

         elif self.pattern_special_command.match(self.stripped_text):
            arguments_string = self.pattern_special_command.sub(r'\1', self.stripped_text)
            this_command, this_file, this_label = self.__read_arguments_from_special_command(arguments_string)

            self.environment = this_command
            self.label = this_label
            if this_command == "insert_fig":
               self.img = this_file
            elif this_command == "insert_file":
               self.data = this_file






   def __read_arguments_from_special_command(self, arguments_string):
      arguments = arguments_string.split(',')

      this_command = arguments[0].lower()
      if this_command not in ["insert_fig","insert_file"]:
         sys.exit("Error reading line {0}: I can't recognize command '{1}' (should be either 'insert_fig' or 'insert_file')".format(self.line_number, this_command))

      # default values:
      this_file = None
      this_label = None
      for arg in arguments[1:]:
         if "file=" in arg:
            this_file = arg.replace('file=', '')
            this_file = this_file.strip(" ")
         if "label=" in arg:
            this_label = arg.replace('label=', '')
            this_label = this_label.strip(" ")
            this_label = this_label.strip('"')

      return this_command, this_file, this_label






   def __read_arguments_from_block_header(self, arguments_string):
      """
      Takes a string containing the arguments (e.g., 'env=shell, title =lorem_ipsum,
      as_html=True")', and
      - extracts the components from that by separating on comma's
      - trims *all* spaces and (single and double) quotes
      - assigns the values to variables
      - returns these variables

      If required parameters are missed, we quit with an error message.
      Optional parameters get a default value.

      TODO: report progress (also to see better which code block header is invalid)
      TODO: give a more informative error message
      """
      # keep everything between the "<<" and the ">>=", and
      # split the arguments on each comma
      arguments = arguments_string.split(',')
      # remove *all* (not only leading and trailing) spaces and quotes of each argument
      for i in range(len(arguments)):
         arguments[i] = arguments[i].replace(' ', '').replace('"', '').replace("'", '')
      
      this_env, this_title, this_as_html, this_collapse_script, this_collapse_stdout, this_collapse_stderr = self.__extract_fields_from_code_block_arguments(arguments)
      self.__validate_code_block_header_fields(this_env, this_title, this_as_html, this_collapse_script, this_collapse_stdout, this_collapse_stderr)

      return (this_env, this_title, this_as_html, this_collapse_script, this_collapse_stdout, this_collapse_stderr)






   def __extract_fields_from_code_block_arguments(self, arguments):
      """
      Takes a list of arguments, and tries to recognize "env", "title", and
      "as_html".

      Does no validation.

      Returns a tuple with values for this_env, this_title, this_as_html.
      """
      # default values:
      this_env             = None
      this_title           = None
      this_as_html         = False
      this_collapse_script = False
      this_collapse_stdout = True
      this_collapse_stderr = True

      for arg in arguments:
         if "env=" in arg:
            this_env = arg.replace('env=', '')
            this_env = this_env.lower()
         if "title=" in arg:
            this_title = arg.replace('title=', '')
            this_title = this_title.lower()
         if "as_html=" in arg:
            this_as_html = arg.replace('as_html=', '')
            this_as_html = this_as_html.strip(" \t\n")
            if this_as_html.lower() == "t" or this_as_html.lower() == "true":
               this_as_html = True
         if "collapse_script=" in arg:
            this_collapse_script = arg.replace('collapse_script=', '')
            this_collapse_script = this_collapse_script.strip(" \t\n")
            if this_collapse_script.lower() == "t" or this_collapse_script.lower() == "true":
               this_collapse_script = True
         if "collapse_stdout=" in arg:
            this_collapse_stdout = arg.replace('collapse_stdout=', '')
            this_collapse_stdout = this_collapse_stdout.strip(" \t\n")
            if this_collapse_stdout.lower() == "f" or this_collapse_stdout.lower() == "false":
               this_collapse_stdout = False
         if "collapse_stderr=" in arg:
            this_collapse_stderr = arg.replace('collapse_stderr=', '')
            this_collapse_stderr = this_collapse_stderr.strip(" \t\n")
            if this_collapse_stderr.lower() == "f" or this_collapse_stderr.lower() == "false":
               this_collapse_stderr = False
      return this_env, this_title, this_as_html, this_collapse_script, this_collapse_stdout, this_collapse_stderr






   def __validate_code_block_header_fields(self, this_env, this_title, this_as_html, this_collapse_script, this_collapse_stdout, this_collapse_stderr):
      """
      Does some basic validation of the fields in the code block header.

      If something is not valid, we exit the script with an error message.
      """
      # if the required parameters are not found, exit with an error message
      if this_env == None or this_title == None:
         sys.exit("Error line {0}: code block misses required parameters, please correct.".format(self.line_number))

      if this_env != "shell" and this_env != "mothur":
         sys.exit("Error in block header line {0}: the env-flag should be either 'shell' or 'mothur', but not '{1}'".format(self.line_number, this_env))

      if this_title == "":
         sys.exit("Error in block header line {0}: the title-flag can not be empty".format(self.line_number))






   def print_output(self):
      """
      Prints a verbose representation of this object.
      """
      print "SourceFileLine object:"
      print "\t- stripped text: {0}".format(self.stripped_text)
      print "\t- environment: {0}".format(self.environment)
      print "\t- name: {0}".format(self.name)

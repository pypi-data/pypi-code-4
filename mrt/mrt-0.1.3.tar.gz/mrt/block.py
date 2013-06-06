#!/usr/bin/python

from random import randint






class Block():
   def __init__(self):
      self.random_number = randint(100000,999999)






class SingleLineBlock(Block):
   """
   This class represents single-line blocks which are defined in
   the input *.mrt file.  These are (1) to insert an image in the 
   report, or (2) to insert (a link to) a file in the report.

   For example:

   <<insert_file, file="mytable.xls", label="Excel file">>

   is a single-line block

   """
   def __init__(self, environment, data = None, img = None, label = None):
      Block.__init__(self)
      self.block_title = None
      self.environment = environment
      self.data        = data
      self.img         = img
      self.label       = label






class CodeBlock(Block):
   """
   This class represents code blocks (with their output) which are defined in
   the input *.mrt file.
   
   For example:

   <<env=mothur, title=my_code_block>>=
   summary.seqs(fasta=reads.fasta)
   @

   is a code block.
   """

   def __init__(self, block_title, environment, as_html, collapse_script, collapse_stdout, collapse_stderr):
      Block.__init__(self)
      #--------------------------------------#
      # flags from the code block header:    #
      #--------------------------------------#
      self.block_title     = block_title     #
      self.environment     = environment     #
      self.as_html         = as_html         #
      self.collapse_script = collapse_script #
      self.collapse_stdout = collapse_stdout #
      self.collapse_stderr = collapse_stderr #
      #--------------------------------------#

      self.extension = self.get_extension_from_environment(self.environment)
      self.lines = []

      #---------------------------------------#
      # file names of scripts, stdout, stderr #
      #---------------------------------------#
      self.file_name_script   = None          #
      self.file_name_stdout   = None          #
      self.file_name_stderr   = None          #
      self.generate_file_name_script()        #
      self.generate_file_name_stdout()        #
      self.generate_file_name_stderr()        #
      #---------------------------------------#



   def get_extension_from_environment(self, environment):
      if environment == "shell":
         extension = "sh"
      elif environment == "mothur":
         extension = "mothur"
      else:
         extension = "unknown"
      return extension



   def generate_file_name_script(self):
      self.file_name_script = "script_{0}_{1}.{2}".format(self.block_title, self.random_number, self.extension)



   def get_file_name_script(self):
      return self.file_name_script



   def get_base_name(self):
      script_base_name = "script_{0}_{1}".format(self.block_title, self.random_number)
      return script_base_name



   def generate_file_name_stdout(self):
      self.file_name_stdout = self.get_base_name() + ".stdout"



   def generate_file_name_stderr(self):
      self.file_name_stderr = self.get_base_name() + ".stderr"



   def save_script_to_file(self):
      this_file = open(self.file_name_script, 'w')
      for line in self.lines:
         this_file.write(line)

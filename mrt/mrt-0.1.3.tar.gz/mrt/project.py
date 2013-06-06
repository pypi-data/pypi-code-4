#!/usr/bin/python

import os
import sys
import pickle
import shutil
import fileinput

from subprocess import call
from general_functions import *
from sourcefile import *



class Project(object):
   def __init__(self, source_file_name, output_dir_name):
      self.source_file_name = source_file_name
      self.source_file      = SourceFile(self.source_file_name)
      self.output_dir_name  = output_dir_name
      self.html_corpus      = []  # a list of string objects (= lines of text)
      self.blocks           = []  # a list of Block objects

      self.extract_blocks_completed  = False
      self.execute_blocks_completed  = False
      self.generate_report_completed = False






   def get_output_index_file(self):
      """
      Returns the HTML index file name.
      """
      return os.path.join(self.output_dir_name, "index.html")






   def get_output_corpus_file(self):
      """
      Returns the HTML corpus file name (the HTML corpus file contains our
      text and data, but without header, footer, CSS-links, etc.)
      """
      return os.path.join(self.output_dir_name, "corpus.html")






   def get_project_file(self):
      """
      Returns the project file name: the Python pickle file which contains
      the current state of the project.
      """
      return os.path.join(self.output_dir_name, "project.pk")






   def extract_blocks(self):
      """
      This method calls the method (same name) of the SourceFile object.

      That method goes through the source file, extracts code blocks, and
      writes individual scripts from those code blocks.

      A list with the file names of the generated blocks is returned and saved as
      a variable of 'self'
      """
      # copy the template output folder to self.output_dir_name
      self.__create_report_folder()

      print '<mrt> parsing file "{0}"'.format(self.source_file_name)
      self.html_corpus, self.blocks = self.source_file.render_blocks_from_source_file()
      self.extract_blocks_completed = True
      self.__save_this_project()
   





   def execute_blocks(self):
      """
      Executes all scripts in 'self.blocks'.
      """
      for i, this_block in enumerate(self.blocks):

         if this_block.__class__.__name__ == "CodeBlock":
            if this_block.environment in ["mothur","shell"]:
               this_block.save_script_to_file()
               self.__execute_single_code_block(this_block, current_number=(i+1), total_number=len(self.blocks))
               if not this_block.as_html:
                  self.__open_div_code_block_in_html_corpus(this_block)
                  self.__append_code_block_lines_to_html_corpus(this_block, "script")
                  self.__append_code_block_lines_to_html_corpus(this_block, "stdout")
                  self.__append_code_block_lines_to_html_corpus(this_block, "stderr")
                  self.__close_div_code_block_in_html_corpus(this_block)
               else:
                  self.__open_div_code_block_in_html_corpus(this_block)
                  self.__append_code_block_lines_to_html_corpus(this_block, "script")
                  self.__append_code_block_lines_to_html_corpus(this_block, "html")
                  self.__append_code_block_lines_to_html_corpus(this_block, "stderr")
                  self.__close_div_code_block_in_html_corpus(this_block)

         elif this_block.__class__.__name__ == "SingleLineBlock":
            if this_block.environment == "insert_fig":
               self.__copy_figure_to_output_dir(this_block)
            elif this_block.environment == "insert_file":
               self.__copy_file_to_output_dir(this_block)
            self.__open_div_single_line_block_in_html_corpus(this_block)
            self.__append_single_line_block_lines_to_html_corpus(this_block)
            self.__close_div_single_line_block_in_html_corpus(this_block)

      self.execute_blocks_completed = True
      self.__save_this_project()






   def generate_report(self):
      """
      Adds output of the code blocks to the report.
      """
      # insert the output of our code blocks in the report
      self.__insert_corpus_into_index_html()
      self.generate_report_completed = True
      self.__save_this_project()






   def __execute_single_code_block(self, this_block, current_number, total_number):
      """
      Reads a single script belonging to a code block
      and executes it.

      TODO: Mothur errors seem not to be redirected to stdout, so we
      will not be able to catch those and stop running the rest of scripts
      
      TODO: probably we should run this inside a try/except environment
      """
      print '<mrt> executing script ({0}/{1}) "{2}"'.format(current_number, total_number, this_block.file_name_script)

      handle_script_stdout = open(this_block.file_name_stdout, 'w')
      handle_script_stderr = open(this_block.file_name_stderr, 'w')

      if this_block.environment == "shell":
         result = call(["bash", this_block.file_name_script], stdout=handle_script_stdout, stderr=handle_script_stderr)
      if this_block.environment == "mothur":
         result = call(["mothur", this_block.file_name_script], stdout=handle_script_stdout, stderr=handle_script_stderr)





   def __copy_figure_to_output_dir(self, single_line_block):
      """
      Check if the file really exists, and
      copy the file to the "img" folder in the report
      """
      print '<mrt> inserting figure "{0}"'.format(single_line_block.img)
      path_from = single_line_block.img
      path_to   = os.path.join(self.output_dir_name, 'img', single_line_block.img)
      copy_file_or_exit(path_from, path_to)






   def __copy_file_to_output_dir(self, single_line_block):
      """
      Check if the file really exists, and
      copy the file to the "data" folder in the report
      """
      print '<mrt> inserting link to file "{0}"'.format(single_line_block.data)
      path_from = single_line_block.data
      path_to   = os.path.join(self.output_dir_name, 'data', single_line_block.data)
      copy_file_or_exit(path_from, path_to)






   def __create_report_folder(self):
      """
      Create the folder which will contain the output HTML
      by copying the template report folder to the
      name given by the user.

      If the folder would already exist, we do not want to take
      the responsibility of deleting it, so we will exit the script
      with an error message.
      """
      print '<mrt> creating output directory "{0}"'.format(self.output_dir_name)
      if not os.path.exists(self.output_dir_name):
         try:
            # what is the path of *this* file ("project.py")?
            # e.g., "/home/pieter/bin/pb/mrt/public/mrt/project.py"
            path_of_this_script = os.path.realpath(__file__)
            # from this path, derive the path to the folder containing the template report folder
            path_of_the_template = os.path.join(
                  os.path.dirname(path_of_this_script),
                  "resources",
                  "template_report"
                  )
            shutil.copytree(path_of_the_template, self.output_dir_name)
         except OSError as exc: # python >2.5
            raise exc
      else:
         sys.exit("Error: there is already a folder '{0}' in your working directory; please remove it first.".format(self.output_dir_name))






   def __open_div_single_line_block_in_html_corpus(self, this_block):
      """
      Adds a new div to the HTML which will contain the single line block
      """
      line_number_to_insert = None
      anchor = "<!-- above: {0} {1} -->".format(this_block.environment, this_block.random_number)
      for i, line_corpus in enumerate(self.html_corpus):
         if anchor in line_corpus:
            line_number_to_insert = i
      self.html_corpus.insert(line_number_to_insert, "<div class='single_line_block_container'>\n")






   def __append_single_line_block_lines_to_html_corpus(self, this_block):
      """
      Adds the HTML for this single-line block
      """
      line_number_to_insert = None
      anchor = "<!-- above: {0} {1} -->".format(this_block.environment, this_block.random_number)
      for i, line_corpus in enumerate(self.html_corpus):
         if anchor in line_corpus:
            line_number_to_insert = i
      if this_block.environment == "insert_fig":
         self.html_corpus.insert(
               line_number_to_insert,
               "{0}: <img class='center_img' src='img/{1}' alt='figure'></img>\n".format(this_block.label, this_block.img)
               )
      if this_block.environment == "insert_file":
         self.html_corpus.insert(
               line_number_to_insert,
               "{0}: <a class='file_link' href='data/{1}' target='_blank'>download link</a>\n".format(this_block.label, this_block.data)
               )







   def __close_div_single_line_block_in_html_corpus(self, this_block):
      """
      Closes the div in the HTML which contains the single line block
      """
      line_number_to_insert = None
      anchor = "<!-- above: {0} {1} -->".format(this_block.environment, this_block.random_number)
      for i, line_corpus in enumerate(self.html_corpus):
         if anchor in line_corpus:
            line_number_to_insert = i
      self.html_corpus.insert(line_number_to_insert, "</div>\n")






   def __open_div_code_block_in_html_corpus(self, this_block):
      """
      Adds a new div to the HTML which will contain the code block
      """
      line_number_to_insert = None
      anchor = "<!-- above: results from file {0} -->".format(this_block.file_name_script)
      for i, line_corpus in enumerate(self.html_corpus):
         if anchor in line_corpus:
            line_number_to_insert = i
      self.html_corpus.insert(line_number_to_insert, "<div class='code_block_container'>\n")






   def __close_div_code_block_in_html_corpus(self, this_block):
      """
      Closes the new div in the HTML which contains the code block
      """
      line_number_to_insert = None
      anchor = "<!-- above: results from file {0} -->".format(this_block.file_name_script)
      for i, line_corpus in enumerate(self.html_corpus):
         if anchor in line_corpus:
            line_number_to_insert = i
      self.html_corpus.insert(line_number_to_insert, "</div>\n")






   def __append_code_block_lines_to_html_corpus(self, this_block, context):
      """
      Goes to the appropriate line in the output HTML file, and
      prepends this line with the contents of the file.

      The file is either:
      - source code (a script),
      - stdout,
      - stderr, or
      - pure HTML (e.g., to insert an image).
      This is given by the parameter "context", which is either "script",
      "stdout", "stderr" or "html".

      TODO: raise an exception if the anchor was not found.
      """
      script_file = this_block.get_file_name_script()
      anchor = "<!-- above: results from file {0} -->".format(this_block.get_file_name_script())
      if context == "script":
         this_title = "Script"
         this_class = "script"
         this_id = "{0}_script".format(this_block.get_base_name())
         this_file_name = this_block.get_file_name_script()
         tag_show_or_hide_div = ' style="display:none"' if ( this_block.collapse_script ) else ''
         tag_show_or_hide_label = 'currently_closed' if ( this_block.collapse_script ) else 'currently_open'
      elif context == "stdout":
         this_title = "Output"
         this_class = "stdout"
         this_id = "{0}_stdout".format(this_block.get_base_name())
         this_file_name = this_block.file_name_stdout
         tag_show_or_hide_div = ' style="display:none"' if ( this_block.collapse_stdout ) else ''
         tag_show_or_hide_label = 'currently_closed' if ( this_block.collapse_stdout ) else 'currently_open'
      elif context == "stderr":
         this_title = "Errors"
         this_class = "stderr"
         this_id = "{0}_stderr".format(this_block.get_base_name())
         this_file_name = this_block.file_name_stderr
         tag_show_or_hide_div = ' style="display:none"' if ( this_block.collapse_stderr ) else ''
         tag_show_or_hide_label = 'currently_closed' if ( this_block.collapse_stderr ) else 'currently_open'
      elif context == "html":
         this_title = "Output"
         this_class = "html_output"
         this_id = "{0}_html_output".format(this_block.get_base_name())
         this_file_name = this_block.file_name_stdout
         tag_show_or_hide_div = ' style="display:none"' if ( this_block.collapse_stdout ) else ''
         tag_show_or_hide_label = 'currently_closed' if ( this_block.collapse_stdout ) else 'currently_open'
      else:
         sys.exit("I don't recognize parameter 'context'")

      #old:
      #tag_show_or_hide_div = '' if ( context == "script" or context == "html" ) else ' style="display:none"'
      #tag_show_or_hide_label = 'currently_open' if ( context == "script" or context == "html" ) else 'currently_closed'

      nr_of_lines = sum(1 for line in open(this_file_name, 'r'))
      line_or_lines = "line" if nr_of_lines == 1 else "lines"

      # at which line number should we insert our code?
      line_number_to_insert = None
      for i, line_corpus in enumerate(self.html_corpus):
         if anchor in line_corpus:
            line_number_to_insert = i

      html_to_be_inserted = []
      html_to_be_inserted.append("<div class='code_block_label_container'>\n")
      if context == "html":
         # showing the number of lines doesn't really make sence here
         html_to_be_inserted.append("<span class='code_block_label {0}' id='{1}'>{2}</span>\n".format(tag_show_or_hide_label, this_id+"_label", this_title))
      else:
         # show the number of lines
         html_to_be_inserted.append("<span class='code_block_label {0}' id='{1}'>{2} ({3} {4})</span>\n".format(tag_show_or_hide_label, this_id+"_label", this_title, nr_of_lines, line_or_lines))
      html_to_be_inserted.append("""<script>
$('#{0}').click(function() {{
   $('#{1}').toggle('fast');
   $('#{0}').toggleClass('currently_open').toggleClass('currently_closed');
}});
</script>
""".format(this_id+"_label", this_id))
      html_to_be_inserted.append("</div>\n")
      html_to_be_inserted.append("<div class='{0}' id='{1}'{2}>\n".format(this_class, this_id, tag_show_or_hide_div))
      for line_script in open(this_file_name, 'r'):
         trimmed_line = line_script[0:800]
         if len(line_script) > 800:
            trimmed_line = trimmed_line + "... (output trimmed)\n"
         html_to_be_inserted.append(trimmed_line)
         #print line_script.replace('\n','<br />\n'),
      html_to_be_inserted.append("</div>\n")

      for this_line in reversed(html_to_be_inserted):
         self.html_corpus.insert(line_number_to_insert, this_line)






   def __insert_corpus_into_index_html(self):
      """
      Takes the corpus HTML (which was generated by executing the individual
      scripts), and inserts it into the main HTML file of the output
      directory.
      """
      print "<mrt> inserting output into the report"
      anchor = "<!-- insert corpus HTML above -->"
      for line_index in fileinput.input(self.get_output_index_file(), inplace=1):
         if anchor in line_index:
            for line_corpus in self.html_corpus:
               print line_corpus,
         print line_index,






   def __save_this_project(self):
      """
      Saves the current Project object to a Python pickle file
      """
      project_file_name = self.get_project_file()
      with open(project_file_name, 'wb') as handle_file_name:
         pickle.dump(self, handle_file_name, pickle.HIGHEST_PROTOCOL)






def load_existing_project_from_output_dir(output_dir_name):
   """
   Loads an instance of the Project class from a Python pickle file in the
   supplied directory
   """
   exit_if_dir_does_not_exist(output_dir_name)
   project_file = os.path.join(output_dir_name, "project.pk")
   this_object = __load_existing_project_from_file(os.path.join(output_dir_name, "project.pk"))
   return this_object






def __load_existing_project_from_file(file_name):
   """
   Reads a Python pickle file which contains an instance of the Project class
   """
   exit_if_file_does_not_exist(file_name)
   with open(file_name, 'rb') as handle_file_name:
      this_object = pickle.load(handle_file_name)
      return this_object

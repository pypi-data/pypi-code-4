#!/usr/bin/python

import sys
import argparse

from general_functions import *






def read_command_line_arguments():
   """
   Read the command line arguments
   """
   parser = argparse.ArgumentParser(
         formatter_class = argparse.RawDescriptionHelpFormatter,
         description     = "Add elements to a (new or existing) module of your report.",
         epilog          = "\n\nWritten by Pieter B.\n"
   )

   #------------------------------------------#
   # file names:                              #
   #------------------------------------------#
   # - input file name (*.mrt file)           #
   # - output directory name                  #
   #------------------------------------------#
   parser.add_argument('-i', '--input', action="store", dest="input_file_name", default=None, required=False, help="Filename of the weaved input document.  Required when you do --run_all (default) or --extract_code_blocks.")
   parser.add_argument('-o', '--output', action="store", dest="output_dir_name", default=None, required=True, help="Name of the directory containing the output HTML code. Always required.")


   #------------------------------------------#
   # which steps of this tool should we run:  #
   # -----------------------------------------#
   # --run_all (default)                      #
   # or one/some of:                          #
   # --extract_code_blocks                    #
   # --execute_code_blocks                    #
   # --generate_report                        #
   #------------------------------------------#
   parser.add_argument('--run_all', action="store_true", dest="run_all", required=False, default=True, help="Perform all steps at once (this is default behaviour).")
   parser.add_argument('--extract_code_blocks', action="store_true", dest="extract_code_blocks", required=False, default=False, help="Only extract code blocks from the input file.  Requires that you supply a project file name to write the current state of the project to (see '--project').")
   parser.add_argument('--execute_code_blocks', action="store_true", dest="execute_code_blocks", required=False, default=False, help="Only run code blocks from the input file.  Assumes that the first step has been performed already.")
   parser.add_argument('--generate_report', action="store_true", dest="generate_report", required=False, default=False, help="Only run the report generation step.  Assumes that previous steps have been performed already.")

   args = parser.parse_args()
   result = {
         'input_file_name'     : args.input_file_name     ,
         'output_dir_name'     : args.output_dir_name     ,
         'run_all'             : args.run_all             ,
         'extract_code_blocks' : args.extract_code_blocks ,
         'execute_code_blocks' : args.execute_code_blocks ,
         'generate_report'     : args.generate_report
         }

   return result






def validate_command_line_arguments(args):
   """
   Validate the command line arguments

   TODO:
   When using only --extract_code_blocks, --execute_code_blocks or --generate_report, we're in a
   danger zone.  Thorough checking of the required parameters and the state of the project object
   will be important.
   For example:
   - when using --execute_blocks, we need a valid Python pickle file for the Project instance
   - when using --execute_blocks, the Project instance needs to have the individual blocks available already
   - ...
   """
   #if args.run_all or args.generate_report: << OBSOLETE ---> from now on: always required
   if args['output_dir_name'] == None:
      raise ArgsException("Error: you need to define an output directory. Quitting")


   # the default value of run_all is True; however,
   # if one of these flags is set, we should set it to False
   # (for example: then we don't necessarily need to have defined an input file)
   if args['extract_code_blocks'] or args['execute_code_blocks'] or args['generate_report']:
      args['run_all'] = False

   if args['run_all'] or args['extract_code_blocks']:
      if args['input_file_name'] == None:
         raise ArgsException("Error: you need to define an input file. Quitting")
      try:
         check_if_file_exists(args['input_file_name'])
      except Exception, e:
         raise ArgsException(e)

   if ( args['execute_code_blocks'] or args['generate_report'] ) and not ( args['extract_code_blocks'] or args['run_all'] ):
      exit_if_dir_does_not_exist(args['output_dir_name'])
   
   return args






def validate_command_line_arguments_or_exit(args):
   try:
      validate_command_line_arguments(args)
   except ArgsException, e:
      sys.exit(e)






class ArgsException(Exception):
   pass

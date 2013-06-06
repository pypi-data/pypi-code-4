#!/usr/bin/python

from args import *
from project import *






def main():
   args = read_command_line_arguments()
   validate_command_line_arguments_or_exit(args)

   #-------------------------------------------------------------------------------#
   # if we start from scratch, then create a new, empty instance of                #
   # our Project class;                                                            #
   # otherwise, load the current state of the project from the Python pickle file  #
   if args['run_all'] or args['extract_code_blocks']:                              #
      my_project = Project(source_file_name  = args['input_file_name'],            #
                           output_dir_name   = args['output_dir_name']             #
                          )                                                        #
   else:                                                                           #
      my_project = load_existing_project_from_output_dir(args['output_dir_name'])  #
   #-------------------------------------------------------------------------------#

   #------------------------------------------------------#
   if args['run_all'] or args['extract_code_blocks']:     #
      my_project.extract_blocks()                         #
                                                          #
   if args['run_all'] or args['execute_code_blocks']:     #
      my_project.execute_blocks()                         #
                                                          #
   if args['run_all'] or args['generate_report']:         #
      my_project.generate_report()                        #
   #------------------------------------------------------#






if __name__ == "__main__":
   main()

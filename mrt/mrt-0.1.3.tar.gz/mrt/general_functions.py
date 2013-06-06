#!/usr/bin/python

import os
import sys
import shutil
import unittest

def check_if_file_exists(file_name):
   """
   Raise an exception if a file with given file name does
   not exist.

   This function is wrapped in 'exit_if_file_does_not_exist()'
   """
   if not os.path.isfile(file_name):
      raise Exception("Error: I could not find file {0}".format(file_name))






def check_if_dir_exists(dir_name):
   """
   Raise an exception if a dir with given dir name does
   not exist.

   This function is wrapped in 'exit_if_dir_does_not_exist()'
   """
   if not os.path.isdir(dir_name):
      raise Exception("Error: I could not find folder {0}".format(dir_name))






def exit_if_file_does_not_exist(file_name):
   """
   If a file (e.g., specified by the command line arguments) does
   not exist, we should show an error message and quit.
   """
   try:
      check_if_file_exists(file_name)
   except Exception,e:
      sys.exit(e)





def exit_if_dir_does_not_exist(dir_name):
   """
   If a dir (e.g., specified by the command line arguments) does
   not exist, we should show an error message and quit.
   """
   try:
      check_if_dir_exists(dir_name)
   except Exception,e:
      sys.exit(e)

def copy_file_or_exit(path_from, path_to):
      # try if we can *find* the file
      exit_if_file_does_not_exist(path_from)
      # try if we can *copy* the file
      try:
         shutil.copyfile(path_from, path_to)
      except:
         sys.exit("Error: I could not copy file '{0}' to '{1}'".format(path_from, path_to))

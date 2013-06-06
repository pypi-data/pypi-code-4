#!/usr/bin/python

import os
import sys
import shutil

from behave import *
from scripttest import TestFileEnvironment





env = TestFileEnvironment('./scratch')



@given(u'the file "{this_file}" does not exist')
def impl(context, this_file):
   try:
      os.remove('./scratch/{0}'.format(this_file))
   except:
      pass



@given(u'the dir "{this_dir}" does not exist')
def impl(context, this_dir):
   this_dir_within_scratch_folder = './scratch/{0}'.format(this_dir)
   if os.path.exists(this_dir_within_scratch_folder):
      try:
         shutil.rmtree(this_dir_within_scratch_folder)
      except:
         print "Exception: ",str(sys.exc_info())



@when(u'I run `{command}`')
def impl(context, command):
   context.result = env.run('./../../../{0}'.format(command), expect_error=True)



@given(u'there is a valid mrt input file named "{input_file}"')
def impl(context, input_file):
   open('./scratch/{0}'.format(input_file),'w').write("<h1>Just a test</h1>")


@given(u'a file named "{input_file}" exists')
def impl(context, input_file):
   open('./scratch/{0}'.format(input_file),'w').write("")



@then(u'I should get a message saying "{this_message}"')
def impl(context, this_message):
   assert this_message in context.result.stdout



@then(u'I should get no error message')
def impl(context):
   print context.result.stderr
   assert context.result.stderr == ""



@then(u'I should get an error message')
def impl(context):
   assert context.result.stderr != ""



@then(u'I should get an error message saying "{this_message}"')
def impl(context, this_message):
   assert this_message in context.result.stderr

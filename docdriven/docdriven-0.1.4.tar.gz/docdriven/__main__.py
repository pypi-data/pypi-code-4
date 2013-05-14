import interface
import testcase
import unittest
import datetime
import os


def read_driven_docs_file(driven_docs_filepath):
    dd_file = open(driven_docs_filepath, 'r')
    for line in dd_file:
        filepath = line.strip()
        if filepath.startswith('#'): continue # skip commented-out lines
        if len(filepath) < 1: continue # skip blank lines
        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, 'DRIVEN_DOCS.txt')
            read_driven_docs_file(filepath)
        else:
            interface.initialize(filepath, debug_output='line_feed')
            print 'docdriven: initializing - '+filepath
            test_case = testcase.init_DocDrivenTestCase(interface.driven_down_doc)
            test_suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            print 'docdriven: running unittest'
            test_suite_result = unittest.TestResult()
            test_suite.run(test_suite_result)
            print 'docdriven: printing to files\n'
            interface.print_to_files(os.path.split(filepath)[0])



print 'docdriven: '+str(datetime.datetime.now())
dd_home = os.environ.get('DOC_DRIVEN_HOME')
if not dd_home:
    dd_home = os.environ.get('HOME')
if not dd_home:
    dd_home = os.path.dirname(os.path.abspath(__file__))
monitor_filename = os.path.join(dd_home, 'DRIVEN_DOCS.txt')
print 'docdriven: '+monitor_filename
read_driven_docs_file(monitor_filename)


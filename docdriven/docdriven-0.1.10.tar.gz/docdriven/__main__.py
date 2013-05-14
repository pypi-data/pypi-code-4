import interface
import testcase
import unittest
import datetime
import os


def read_driven_docs_file(root_dir):
    print 'docdriven: '+root_dir
    dd_file = open(os.path.join(root_dir, 'DRIVEN_DOCS.txt'), 'r')
    for line in dd_file:
        filepath = line.strip()
        if filepath.startswith('#'): continue # skip commented-out lines
        if len(filepath) < 1: continue # skip blank lines
        if os.path.isdir(filepath):
            read_driven_docs_file(filepath)
        else:
            interface.initialize(os.path.join(root_dir, filepath), debug_output='line_feed')
            print 'docdriven: initializing - '+os.path.join(root_dir, filepath)
            test_case = testcase.init_DocDrivenTestCase(interface.driven_doc)
            test_suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            print 'docdriven: running unittest'
            test_suite_result = unittest.TestResult()
            test_suite.run(test_suite_result)
            print 'docdriven: printing to files\n'
            interface.print_to_files(root_dir)



print 'docdriven: '+str(datetime.datetime.now())
dd_home = os.environ.get('DOC_DRIVEN_HOME')
if not dd_home:
    dd_home = os.environ.get('HOME')
if not dd_home:
    dd_home = os.path.dirname(os.path.abspath(__file__))
read_driven_docs_file(dd_home)


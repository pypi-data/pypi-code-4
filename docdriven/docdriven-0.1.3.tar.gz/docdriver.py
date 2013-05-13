from docdrivendev import interface
from docdrivendev import testcase
import unittest
import datetime
import os

print 'dddriver: '+str(datetime.datetime.now())

monitor_filename = os.path.dirname(os.path.abspath(__file__))+'/monitor.txt'
monitor_file = open(monitor_filename, 'r')
for line in monitor_file:
    # print 'dddriver: found line: '+line.strip()
    filepath = line.strip()
    if filepath.startswith('#'): continue # skip commented-out lines
    if len(filepath) < 1: continue # skip blank lines
    interface.initialize(filepath, print_feed=True)

    print 'dddriver: initializing - '+filepath
    test_case = testcase.init_DocDrivenTestCase(interface.driven_down_doc)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
    print 'dddriver: running unittest'
    test_suite_result = unittest.TestResult()
    test_suite.run(test_suite_result)

    print 'dddriver: printing to files\n'
    interface.print_to_files(os.path.split(filepath)[0])
    # print 'dddriver: finished\n'


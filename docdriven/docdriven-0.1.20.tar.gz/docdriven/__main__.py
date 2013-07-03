import unittest
import os
import logging
import sys
import subprocess

import interface
import testcase

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
root = logging.getLogger()

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)25s - %(levelname)7s - %(message)s',"%m-%d %H:%M")
ch.setFormatter(formatter)
root.addHandler(ch)

def drive_dd_file(dd_file_full_path):
    docdriven_interface = interface.get_docdriven_interface(dd_file_full_path, debug_output='file_line_feed')
    test_case = testcase.get_docdriven_testcase(docdriven_interface)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
    log.debug('running unittest')
    text_test_runner = unittest.TextTestRunner(stream=sys.stdout, descriptions=True, verbosity=2)
    test_suite_result = text_test_runner.run(test_suite)
    print test_suite_result
    log.debug('printing to files')
    interface.print_to_files(docdriven_interface, include_response=True)


def read_driven_docs_file(root_dir):
    log.debug('root_dir: '+root_dir)
    dd_filename = os.path.join(root_dir, 'DRIVEN_DOCS.txt')
    log.debug('trying to open: '+dd_filename)
    with open(dd_filename) as driven_docs_file:
        log.debug('looping through lines in: '+dd_filename)
        for line in driven_docs_file:
            filepath = line.strip()
            if filepath.startswith('!'): continue # skip commented-out lines
            if len(filepath) < 1: continue # skip blank lines
            log.debug('this line should be a filepath: '+filepath)
            if os.path.isdir(filepath):
                log.debug('found directory filepath - '+filepath)
                read_driven_docs_file(filepath)
            else:
                head, tail = os.path.split(filepath)
                if head is None or len(head)<1:
                    log.debug('no root_dir in the filepath - using root_dir: '+root_dir)
                    full_filepath = os.path.join(root_dir, tail)
                else:
                    full_filepath = filepath
                log.debug('found normal full_filepath; initializing interface: '+full_filepath)
                drive_dd_file(full_filepath)


dd_home = os.environ.get('DOC_DRIVEN_HOME')
if not dd_home:
    dd_home = os.path.dirname(os.path.abspath(__file__))
if not dd_home:
    dd_home = os.environ.get('HOME')
read_driven_docs_file(dd_home)
subprocess.call('/Users/Jon/dev/docdriven/publisher.sh')



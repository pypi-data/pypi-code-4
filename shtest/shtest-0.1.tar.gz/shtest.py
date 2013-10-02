#!/usr/bin/env python
"""The shtest tool is able to run executable scripts as tests and
create a junit compatible xml report.

The scripts are excuted sequentially and started and runs that
do not exit with 0 are reported as failures.
"""
import os
import re
import shutil
import subprocess
import tempfile
import time
import sys
import argparse


__VERSION__ = "0.1"

_TEST_FILE_PATTERN = r'.*test[s]?.*'


class TestCase(object):
    """Test case wrapper class that is used to store the results of
    a single test run
    """
    def __init__(self, name):
        #: the name of the test
        self.name = name
        #: the stdout content of the test
        self.out = None
        #: the stderr content of the test
        self.err = None
        #: the time in seconds
        self.time = 0.0
        #: general state of the test
        self.passed = False


def write_xml_results(test_cases, target="shtest.xml"):
    """Write the given list of test cases as JUnit compatible xml output.
    By default output is written to `shtest.xml`.

    :param test_cases: the list of test cases
    :param target: target file name
    """
    with open(target, 'w') as out:
        fails = sum(map(lambda t: 0 if t.passed else 1, test_cases))
        out.write('<testsuite '
                  'failures="%d" '
                  'errors="0" '
                  'skips="0" '
                  'tests="%d" '
                  'time="%.3f">\n' % (fails, len(test_cases),
                                      sum([t.time for t in test_cases])))
        for t in test_cases:
            out.write('<testcase classname="bash" name="%s" '
                      'time="%.3f">\n' % (t.name, t.time))
            if not t.passed:
                out.write("<failure message='' "
                          "type=''><![CDATA[%s]]>" % (t.err))
                out.write("\n</failure>\n")
            out.write('<system-out>\n'
                      '<![CDATA[%s]]>\n</system-out>\n' % (t.out))
            out.write('<system-err>\n'
                      '<![CDATA[%s]]>\n</system-err>\n' % (t.err))
            out.write("</testcase>\n")
        out.write('</testsuite>\n')
        out.close()


def run_test(name, cwd=False, status=None):
    """Executes the script with the given anme and returns a TestCase.

    Each test case gets its own TEST_DIR environment variable that
    contains the absolute path to a temporary directory created for
    a test. The directory is automatically removed after the test execution.

    :param name: the name of the script to run
    :param status: do not print status information. If the value is
                   ".", simple status is printed, otherwise, full status
                   is printed
    :param cwd: change the working directory to the parent folder of the test
                script
    """
    if status and status != ".":
        sys.stderr.write("Execute %s : " % (name))
    testcase = TestCase(name)
    try:
        tmp_dir = tempfile.mkdtemp()
        start_time = time.time()
        process = subprocess.Popen(
            [os.path.abspath(name)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                "TEST_DIR": tmp_dir
            },
            cwd=os.getcwd() if not cwd else os.path.dirname(
                os.path.abspath(name)),
            shell=False
        )
        (testcase.out, testcase.err) = process.communicate()
        testcase.passed = process.wait() == 0
        testcase.time = time.time() - start_time
    except:
        testcase.passed = False
    finally:
        if tmp_dir is not None:
            shutil.rmtree(tmp_dir)
        if status:
            if status != ".":
                msg = "PASS" if not testcase.passed else "FAIL"
                print >>sys.stderr, "%.3f\t\t%s" % (testcase.time, msg)
            else:
                sys.stderr.write("." if testcase.passed else "F")
    return testcase


def _is_test_case(name):
    """Returns true if the given name is a path to an executable test
    case that follows the test case pattern.
    """
    if not os.path.isfile(name) or not os.path.exists(name):
        return False
    if not re.search(_TEST_FILE_PATTERN, name):
        return False
    # check if file is executable
    if not os.access(name, os.X_OK):
        return False
    return True


def _search_for_tests(path):
    """Yields test cases in the given directory"""
    for root, dirs, files in os.walk(path):
        for name in files:
            script = os.path.join(root, name)
            if _is_test_case(script):
                yield script


def main():
    parser = argparse.ArgumentParser(prog="sh.test")
    parser.add_argument(
        "files", nargs="*",
        help="""Tests to execute. By default, the current
        working directory is searched for *test[s]* files.
        Youn either specify a list of folders or explicit
        files here. Test files have to be executable to
        be detected as valid tests."""
    )
    parser.add_argument("--version", action='version',
                        version="%(prog)s " + __VERSION__)
    parser.add_argument('--xml',
                        nargs="?",
                        default=None,
                        const='shtest.xml',
                        help="Write xml output")
    parser.add_argument('--cwd',
                        action="store_true",
                        help="""Change the working directory for
                        each test to the parent folder of the test. By default
                        all test are executed in the current working directory
                        """)
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help="""Print verbose output """)
    args = parser.parse_args()

    ################################################################
    # Run the tests
    ################################################################
    test_cases = []
    if not args.files:
        args.files = [os.getcwd()]
    status = "." if not args.verbose else "all"
    for path in args.files:
        if _is_test_case(path):
            test_cases.append(run_test(path, cwd=args.cwd, status=status))
        elif os.path.isdir(path):
            for script in _search_for_tests(path):
                test_cases.append(run_test(script,
                                           cwd=args.cwd, status=status))

    ################################################################
    # Print errors and XML results
    ################################################################
    if status == ".":
        print >> sys.stderr, ""
    for t in test_cases:
        if not t.passed:
            head = "Failed test %s" % (t.name)
            print >> sys.stderr, ""
            print >> sys.stderr, head
            print >> sys.stderr, "-" * len(head)
            print >> sys.stderr, "Output:"
            print >> sys.stderr, t.out
            print >> sys.stderr, "Error output:"
            print >> sys.stderr, t.err
    if args.xml:
        write_xml_results(test_cases, args.xml)


if __name__ == "__main__":
    main()

import sys
import subprocess
import re


def iterate_tests(test_suite_or_case):
    """Iterate through all of the test cases in 'test_suite_or_case'."""
    try:
        suite = iter(test_suite_or_case)
    except TypeError:
        yield test_suite_or_case
    else:
        for test in suite:
            for subtest in iterate_tests(test):
                yield subtest


def test_list(suite):
    tdata = []
    for tfunc in iterate_tests(suite):
        tname = '%s.%s' % (tfunc.__class__.__name__,
                           tfunc._testMethodName)
        extra = ''
        if getattr(tfunc, '__unittest_skip__', False):
            extra = tfunc.__unittest_skip_why__
        else:
            if getattr(getattr(tfunc, tfunc._testMethodName),
                       '__unittest_skip__', False):
                extra = getattr(tfunc,
                                tfunc._testMethodName
                                ).__unittest_skip_why__

        extra = 'no' if not len(extra) else 'yes: ' + extra
        tdata.append((tname,
                      tfunc.__class__.__module__,
                      extra))
    return tdata


def findout_terminal_width(defaultwidth=20):
    if hasattr(sys.stdout, 'isatty') and not sys.stdout.isatty():
        return defaultwidth
    try:
        process = subprocess.Popen(['stty', '-a'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout = process.stdout.read()
        if sys.version_info[0] > 2:
            stdout = stdout.decode("utf-8")
    except (OSError, IOError):
        pass
    else:
        # We support the following output formats from stty:
        #
        # 1) Linux   -> columns 80
        # 2) OS X    -> 80 columns
        # 3) Solaris -> columns = 80

        re_linux = r"columns\s+(?P<columns>\d+);"
        re_osx = r"(?P<columns>\d+)\s*columns;"
        re_solaris = r"columns\s+=\s+(?P<columns>\d+);"

        for regex in (re_linux, re_osx, re_solaris):
            match = re.search(regex, stdout)

            if match is not None:
                columns = match.group('columns')
                try:
                    return int(columns)
                except ValueError:
                    pass
    return defaultwidth

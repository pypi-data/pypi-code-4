
import random
import sys
import os.path
import unittest

import xmlrunner

# Patch xmlrunner to prevent addSkip failure

def __init__(self, test_result, test_method, 
             outcome=xmlrunner._TestInfo.SUCCESS, err=None):
    self.test_result = test_result
    self.outcome = outcome
    self.elapsed_time = 0
    self.err = err or ''

    self.test_description = self.test_result.getDescription(test_method)
    self.test_exception_info = (
        self.err if isinstance(self.err, basestring)
        else self.test_result._exc_info_to_string(
                self.err, test_method)
    )

    self.test_name = xmlrunner.testcase_name(test_method)
    # FIXME: In practice id method might be overridden
    self.test_id = test_method.__class__.id(test_method)

xmlrunner._TestInfo.__init__ = __init__

def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1,
             elapsed_times=True):
    unittest._TextTestResult.__init__(self, stream, descriptions, verbosity)
    self.successes = []
    self.skipped = getattr(self, 'skipped', None) or []
    self.callback = None
    self.elapsed_times = elapsed_times

xmlrunner._XMLTestResult.__init__ = __init__

del __init__

def junitrunner():
    report_path = os.path.join(os.environ.get('BUILD_REPORT', '.'), 'xunit')
    print report_path
    return xmlrunner.XMLTestRunner(output=report_path)

def unix_alloc_socket(socket_type, (port_low, port_high)):
    def parse_tcp(f):
        for l in f :
            hexport = l.lstrip().split(' ', 3)[1].split(':', 2)[1]
            yield int(hexport, 16)
    parsers = dict([k[6:],v] for k,v in locals().iteritems() \
                             if k.startswith('parse_'))
    if socket_type not in parsers:
        raise ValueError('Unsupported socket type ' + socket_type)
    fsockets = open('/proc/net/' + socket_type, 'rb')
    try :
        fsockets.readline()       # Skip header
        ports = tuple(parsers[socket_type](fsockets))
        port = random.randrange(port_low, port_high)
        while port in ports :
            port = random.randrange(port_low, port_high)
        return port
    finally :
        fsockets.close()


import nanotest.core as nc
import nanotest.injection as ni

class Nanotester:
    """Initialize a nanotest tester object."""
    def __init__(self):
        self.version   = "2.1.0"
        self.results   = [] # test results go here
        self.nodestack = [] # used to build hash for struct compares
        self.xhash = {}     # experimental struct hash
        self.ghash = {}     # given struct hash
        self.injt = None
        self.injf = None

    def test(self, xpmtl, given, msg, invert=False):
        """Test two values for equality"""
        if type(xpmtl) != type(given):
            res = nc.result(False, type(given), type(xpmtl), msg, "Types don't match")
            self.results.append(res)
        elif isinstance(xpmtl, (tuple, list, dict)):
            nc.deepcomp(self, xpmtl, given, msg, invert)
        else:
            passed, reason = nc.comp(self, xpmtl, given, msg, invert)
            self.results.append(nc.result(passed, given, xpmtl, msg, reason))
                
    def untest(self, xpmtl, given, msg):
        """Test two values for inequality"""
        self.test(xpmtl, given, msg, invert=True)

    def inject(self, filename):
        """Source API tests from a given file"""
        ni.source(self, filename)

    def itest(self, testname, xpmtl, invert=False):
        """Run an injected test for equality"""
        # handle failures
        if not testname in self.injt:
            res = nc.result(False, None, xpmtl, "Injected test {} not found".format(testname), file=self.injf)
            self.results.append(res)
            return
        self.test(xpmtl, self.injt[testname][0], testname[1], invert)

    def unitest(self, testname, xpmtl):
        """Run an injected test for inequality"""
        self.itest(testname, xpmtl, invert=True)

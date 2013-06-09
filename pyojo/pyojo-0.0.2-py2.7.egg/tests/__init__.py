# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Tests for the pyojo package.

"""

import os
import sys
import time
import unittest
import logging
import pyojo
from pyojo import Config
from pyojo.server import HTTPD
import basic
import request
import browser

PATH = os.path.abspath(os.path.dirname(__file__))
pyojo.Config.url = os.path.join(PATH, "browser", "srv")


def main():
    
    #logging.basicConfig(filename=log_file, stream=sys.stderr )
    _stdout = sys.stdout
    _stderr = sys.stderr
    log_file = os.path.join(os.getcwd(),'test.txt')
    sys.stdout = open(log_file, 'w')
    sys.stderr = sys.stdout    
    now = time.time()
    
    title = "PYOJO TEST SUITE RESULTS %s" % pyojo.timestamp(now)
    print title
    print "-"*len(title)+"\n"
    
    result ={}
    
    print "\n"+"#"*79
    print "BASIC TESTS"
    print "#"*79
    suite = unittest.TestLoader().loadTestsFromModule(basic)
    result["basic"] = unittest.TextTestRunner(verbosity=2, 
                                              stream=sys.stdout).run(suite)
    
    print "\n"+"#"*79
    print "REQUEST TESTS"
    print "#"*79
    suite = unittest.TestLoader().loadTestsFromModule(request)
    result["request"] = unittest.TextTestRunner(verbosity=2,
                                                stream=sys.stdout).run(suite)
    
    print "\n"+"#"*79
    print "BROWSER TESTS"
    print "#"*79
    suite = unittest.TestLoader().loadTestsFromModule(browser)
    Config.url = os.path.join(PATH, "browser", "srv")
    httpd = HTTPD()
    httpd.start()
    result["browser"] = unittest.TextTestRunner(verbosity=2,
                                                stream=sys.stdout).run(suite)
    httpd.stop()
    
    txt = "\n"+"="*79+"\n\n"
    testsRun = 0
    errors = []
    failures = []
    for name, res in result.iteritems():
        testsRun += res.testsRun
        failures += res.failures
        errors += res.errors
    
    txt += "pyojo test suite ran %s tests in %i seconds\n\n" % (testsRun,
                                                        time.time() - now) 
    if len(errors)+len(failures)==0: 
        txt += "PASSED OK\n"
    else:
        if len(errors)>0:
            title = "%s ERRORS:" % len(errors)
            txt += title + "\n"
            txt += "-"*len(title) + "\n"
            for cls, trace in errors:
                txt += "* %s\n\n" % cls
                txt += "%s\n" % trace
        if len(failures)>0:
            title = "%s FAILURES:" % len(failures)
            txt += title + "\n"
            txt += "-"*len(title) + "\n"
            for cls, trace in failures:
                txt += "* %s\n\n" % cls
                txt += "%s\n" % trace
                
    txt += "\n"+"="*79+"\n"
    
    print txt
    sys.stdout = _stdout
    sys.stderr = _stderr
    print txt
    
if __name__=='__main__':
    main()

    
    
    
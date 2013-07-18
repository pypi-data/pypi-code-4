#-*- coding: utf-8 -*-
import os
import sys
import time
import logging
import StringIO
import traceback

import nose
import nose.util

from nose.plugins import Plugin

import nosexunitlite.core as ncore
import nosexunitlite.const as nconst
import nosexunitlite.tools as ntools
import nosexunitlite.excepts as nexcepts

# Get a logger
logger =  logging.getLogger('%s.%s' % (nconst.LOGGER, __name__))

class NoseXUnitLite(Plugin, object):

    def help(self):
        '''Help'''
        return 'Output XML report of test status'

    def options(self, parser, env=os.environ):
        '''Add launch options for NoseXUnitLite'''
        # Call super
        Plugin.options(self, parser, env)
        # ---------------------------------------------------------------------
        # CORE
        # ---------------------------------------------------------------------
        # Add test target folder
        parser.add_option('--core-target',
                          action='store',
                          default = nconst.TARGET_CORE,
                          dest='core_target',
                          help='Output folder for test reports (default is %s).' % nconst.TARGET_CORE)
        # Add source folder
        parser.add_option('--source-folder',
                          action='store',
                          default=None,
                          dest='source',
                          help='Set source folder (optional). Add folder in sys.path.')
        # Search sources in source tree
        parser.add_option('--search-source',
                          action='store_true',
                          default=False,
                          dest='search_source',
                          help="Walk in the source folder to add deeper folders in sys.path if they don't contain __init__.py file. Works only if --source-folder is defined.")
        # Search tests in 
        parser.add_option('--search-test',
                          action='store_true',
                          default=False,
                          dest='search_test',
                          help='Search tests in folders with no __init__.py file (default: do nothing).')
    
    def configure(self, options, config):
        '''Configure the plug in'''
        # Call super
        Plugin.configure(self, options, config)
        # ---------------------------------------------------------------------
        # NOSE
        # ---------------------------------------------------------------------
        # Store the configuration
        self.config = config
        # Check if processes enabled
        try: self.fork = 1 != max(int(options.multiprocess_workers), 1)
        # If multiprocess not available
        except: self.fork = False
        # ---------------------------------------------------------------------
        # CORE
        # ---------------------------------------------------------------------
        # Store test target folder
        self.core_target = os.path.abspath(options.core_target)
        # Store source folder
        if options.source: self.source = os.path.abspath(options.source)
        else: self.source = None
        # Check if has to search sources
        self.search_source = options.search_source
        # Check if has to search tests
        self.search_test = options.search_test
    
    def initialize(self):
        '''Set the environment'''
        # Check that source folder exists if specified
        if self.source and not os.path.isdir(self.source):
            # Source folder doesn't exist
            raise nexcepts.NoseXUnitError("source folder doesn't exist: %s" % self.source)
        # Create the core target folder
        ntools.create(self.core_target)
        # Clean the target folder of the core
        ntools.clean(self.core_target, nconst.PREFIX_CORE, nconst.EXT_CORE)
        # Initialize the packages
        self.packages = {}
        # Add the source folder in the path
        if self.source:
            # Get the packages
            self.packages = ntools.packages(self.source, search=self.search_source)
            # Get the folders to add in the path
            folders = []
            # Go threw the packages
            for package in self.packages.keys():
                # Check if is as sub package or a sub module
                if package.find('.') == -1:
                    # Get the folder
                    folder = os.path.dirname(self.packages[package])
                    # If not already in, add it
                    if folder not in folders: folders.append(folder)
            # Get current path
            backup = sys.path
            # Clean up
            sys.path = []
            # Add to the path
            for folder in folders:
                # Log
                logger.info('add folder in sys.path: %s' % folder)
                # Add to the path
                sys.path.append(folder)
            # Add old ones
            sys.path.extend(backup)

    def enable(self, package):
        '''Check if a package has to be processed'''
        # Check if is a test
        if self.conf.testMatch.search(package): return False
        return True

    def begin(self):
        '''Initialize the plug in'''
        # Initialize plug in
        self.initialize()
        # Store the module
        self.module = None
        # Store the suite
        self.suite = None
        # Store the start time
        self.start = None
        # Get a STDOUT recorder
        self.stdout = ncore.StdOutRecoder()
        # Get a STDERR recorder
        self.stderr = ncore.StdErrRecorder()

    def wantDirectory(self, dirname):
        '''Check if search tests in this folder'''
        # Check if search test option enable and if there is no __init__ in the folder
        if self.search_test and not os.path.exists(os.path.join(dirname, nconst.INIT)): return True
        # Else I don't care
        else: return

    def enableSuite(self, test):
        '''Check that suite exists. If not exists, create a new one'''
        # Get the current module
        current = ntools.get_test_id(test).split('.')[0]
        # Check if this is a new one
        if self.module != current:
            # Set the new module
            self.module = current
            # Stop the previous suite
            self.stopSuite()
            # Start a new one
            self.startSuite(self.module)

    def startSuite(self, module):
        '''Start a new suite'''
        # Create a suite
        self.suite = ncore.XSuite(module)
        # Start it
        self.suite.start()
        # Clean STDOUT
        self.stderr.reset()
        # Clean STDERR
        self.stdout.reset()
        # Start recording STDOUT
        self.stderr.start()
        # Start recording STDERR
        self.stdout.start()
   
    def startTest(self, test):
        '''Record starting time'''
        # Enable suite
        self.enableSuite(test)
        # Get the start time
        self.start = time.time()

    def addTestCase(self, kind, test, err=None):
        '''Add a new test result in the current suite'''
        # Create a test
        elmt = ncore.XTest(kind, test, err=err)
        # Set the start time
        elmt.setStart(self.start)
        # Set the stop time
        elmt.stop()
        # Enable the suite
        self.enableSuite(test)
        # Add test to the suite
        self.suite.addTest(elmt)

    def addError(self, test, err):
        '''Add a error test'''
        # Get the king of error
        kind = nconst.TEST_ERROR
        # Check if skipped
        if isinstance(test, nose.SkipTest): kind = nconst.TEST_SKIP
        # Check if useless
        elif isinstance(test, nose.DeprecatedTest): kind = nconst.TEST_DEPRECATED
        # Add the test
        self.addTestCase(kind, test, err=err)

    def addFailure(self, test, err):
        '''Add a failure test'''
        self.addTestCase(nconst.TEST_FAIL, test, err=err)

    def addSuccess(self, test):
        '''Add a successful test'''
        self.addTestCase(nconst.TEST_SUCCESS, test)

    def stopSuite(self):
        '''Stop the current suite'''
        # Check if a suite exists
        if self.suite != None:
            # Stop recording on STDOUT
            self.stdout.stop()
            # Stop recording on STDERR
            self.stderr.stop()
            # Stop the suite
            self.suite.stop()
            # Affect recorded STDOUT to the suite
            self.suite.setStdout(self.stdout.content())
            # Affect recorded STDERR to the suite
            self.suite.setStderr(self.stderr.content())
            # Create XML
            self.suite.writeXml(self.core_target)
            # Clean the suite
            self.suite = None

    def report(self, stream):
        '''Create the report'''

    def consider(self, entry, package):
        '''Check if the package as to be covered'''
        # Check if skipped
        if entry in self.skipped: return False
        # Check if has a __file__ attribute
        if not hasattr(package, '__file__'): return False
        # Get the path
        path = nose.util.src(package.__file__)
        # Check path
        if not path or not path.endswith('.py'): return False
        # Go threw the packages
        if entry in self.cover_packages: return True
        # Exclude by default
        return False

    def finalize(self, result):
        '''Set the old standard outputs'''
        # Stop the current suite
        self.stopSuite()
        # Clean STDOUT recorder
        self.stderr.end()
        # Clean STDERR recorder
        self.stdout.end()
        # Check if fork
        if self.fork:
            # Results not directly collected, available only there
            fork_suite = ncore.XSuite('multiprocess')
            # Create a fake id for successful tests
            class FakeTest(object):
                # Store unique success ID
                def __init__(self, pos): self.pos = pos
                # Add ID function
                def id(self): return 'nose.multiprocess.success%d' % self.pos
            # Add success
            for i in range(result.testsRun): fork_suite.addTest(ncore.XTest(nconst.TEST_SUCCESS, FakeTest(i)))
            # Add errors
            for test, err in result.errors: fork_suite.addTest(ncore.XTest(nconst.TEST_ERROR, test, err=err))
            # Add failures
            for test, err in result.failures: fork_suite.addTest(ncore.XTest(nconst.TEST_FAIL, test, err=err)) 
            # Write
            fork_suite.writeXml(self.core_target)

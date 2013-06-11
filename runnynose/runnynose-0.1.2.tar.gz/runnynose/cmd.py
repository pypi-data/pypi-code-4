import copy
import os
import pickle
import subprocess
import sys

import pyinotify

import nose

from runnynose.tracker import DependencyTracker
from runnynose.plugin import COMM_FILE
from runnynose.plugin import TestCollectorPlugin
from runnynose.plugin import TestContextPlugin
from runnynose.util import NotSpecified

class TestRunner(object):
    
    def __init__(self, argv):
        self._argv = argv
        self._tracker = DependencyTracker.get()
        self._orphans = set()
    
    def start(self):
        self._run()
    
    def handle_changed(self, pathname):
        test_addresses = self._collect(pathname)
        for address in test_addresses:
            if address[2]:
                self._tracker.add(address[0], address)
        
        old_tests = set([test for test in self._tracker.dependencies_of(pathname)
                         if test[0] == pathname])
        new_tests = test_addresses
        deleted_tests = old_tests - new_tests
        for test in deleted_tests:
            self._tracker.remove_test(test)
        
        tests = self._tracker.dependencies_of(pathname)
        if tests:
            tests.update(self._orphans)
            test_ids = [':'.join(address[1:]) for address in tests]
            self._run(list(test_ids))
    
    def handle_deleted(self, pathname):
        tests = self._tracker.dependencies_of(pathname)
        deleted_tests = set()
        for address in tests:
            if address[0] == pathname:
                deleted_tests.add(address)
                if address in self._orphans:
                    self._orphans.remove(address)
        for address in deleted_tests:
            self._tracker.remove_test(address)
        
        tests = self._tracker.dependencies_of(pathname)
        self._orphans.update(tests)
        if tests:
            test_ids = [':'.join(address[1:]) for address in tests]
            self._run(list(test_ids))
    
    def _run(self, test_ids=NotSpecified):
        if test_ids is NotSpecified:
            test_ids = []
        
        argv = self._argv + ['--with-runnynose-test-context'] + test_ids
        argv[0] = 'nosetests'
        subprocess.call(argv)
        with open(COMM_FILE, 'r') as f:
            result = pickle.load(f)
        self._tracker.load(result['dependencies'])
        for test in result['passed']:
            if test in self._orphans:
                self._orphans.remove(test)
    
    def _collect(self, pathname):
        with open('/dev/null', 'w') as nowhere:
            argv = self._argv+['--collect-only', '--with-runnynose-test-collector'] + [pathname]
            argv[0] = 'nosetests'
            subprocess.call(argv, stdout=nowhere, stderr=nowhere)
        with open(COMM_FILE, 'r') as f:
            test_ids = pickle.load(f)
        return test_ids

class Watcher(pyinotify.ProcessEvent):
    
    def my_init(self, runner, argv):
        self._runner = runner
        self._argv = copy.copy(argv)
    
    def _is_python_source(self, pathname):
        basename = os.path.basename(pathname)
        if basename.startswith('.#'):
            return False
        if basename.endswith('.py'):
            return True
        else:
            return False
    
    def process_IN_CLOSE_WRITE(self, event):
        if self._is_python_source(event.pathname):
            print 'CHANGED: ', event.pathname
            self._runner.handle_changed(event.pathname)
    
    def process_IN_DELETE(self, event):
        if self._is_python_source(event.pathname):
            print 'DELETED:', event.pathname
            self._runner.handle_deleted(event.pathname)

def main(argv=NotSpecified):
    if argv is NotSpecified:
        argv = sys.argv
    
    runner = TestRunner(argv)
    runner.start()
    
    # print DependencyTracker.get().__dict__
    wm = pyinotify.WatchManager()
    watcher = Watcher(runner=runner, argv=argv)
    notifier = pyinotify.Notifier(wm, default_proc_fun=watcher)
    wm.add_watch(os.getcwd(), pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    notifier.loop()


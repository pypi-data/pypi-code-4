from pickle import dump

from astkit import install_processor

from nose.plugins import Plugin

from runnynose.hook import TrackingTransformer
from runnynose.tracker import DependencyTracker

COMM_FILE = '.runnynose'

class TestContextPlugin(Plugin):
    name='runnynose-test-context'
    
    def begin(self):
        install_processor(TrackingTransformer())
        self._passed = set()
    
    def startTest(self, test):
        pathname = test.address()[0]
        current_address = test.address()
        DependencyTracker.get().add(pathname, current_address)
        DependencyTracker.current_test = current_address
        self._passed.add(current_address)
    
    def handleError(self, test, err):
        self._passed.remove(test.address())
    handleFailure = handleError
    
    def stopTest(self, test):
        DependencyTracker.current_test = None
        
    def report(self, stream):
        result = {'dependencies': DependencyTracker.get().dump(),
                  'passed': self._passed}
        with open(COMM_FILE, 'w') as f:
            dump(result, f)
    
class TestCollectorPlugin(Plugin):
    name='runnynose-test-collector'
    
    def __init__(self, *args, **kwargs):
        super(TestCollectorPlugin, self).__init__(*args, **kwargs)
        self.tests = set()
    
    def startTest(self, test):
        self.tests.add(test.address())
    
    def report(self, stream):
        with open(COMM_FILE, 'w') as f:
            dump(self.tests, f)
        return True

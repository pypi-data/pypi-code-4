import inspect

from astkit import ast

def get_setup():
    source = inspect.getsource(DependencyTracker.get_tracker)
    source = "\n".join([line[4:] for line in source.splitlines()])
    mod = ast.parse(source)
    defn = mod.body[0]
    setup = defn.body[:]
    for stmt in setup:
        stmt.lineno -= 1
    return setup

def get_record():
    source = inspect.getsource(DependencyTracker.record_use)
    source = "\n".join([line[4:] for line in source.splitlines()])
    mod = ast.parse(source)
    defn = mod.body[0]
    record = defn.body[:]
    for stmt in record:
        stmt.lineno -= 1
    return record
    
class DependencyTracker(object):
    current_test = None
    
    _instance = None
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._dependencies = {}
    
    def add(self, pathname, address):
        if address:
            addresses = self._dependencies.setdefault(pathname, set())
            addresses.add(address)
    
    def dependencies_of(self, pathname):
        return self._dependencies.get(pathname, set())
    
    def depends_on(self, address):
        pathnames = set()
        for pathname, addresses in self._dependencies.items():
            if address in addresses:
                pathnames.add(pathname)
        return pathnames
    
    def remove_test(self, address):
        for pathname in self.depends_on(address):
            self._dependencies[pathname].remove(address)
    
    # Dumping and loading methods
    def dump(self):
        return self._dependencies
    
    def load(self, dependencies):
        for pathname, addresses in dependencies.items():
            for address in addresses:
                self.add(pathname, address)
    
    # These are for instrumented code to call
    def record_pathname(self, pathname):
        self.add(pathname, self.current_test)
    
    @classmethod
    def get_tracker(cls):
        from runnynose.tracker import DependencyTracker
        tracker = DependencyTracker.get()
    
    @classmethod
    def record_use(cls):
        tracker.record_pathname(__file__)

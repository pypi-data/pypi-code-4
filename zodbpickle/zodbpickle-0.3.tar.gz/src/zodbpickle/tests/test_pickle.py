import io
import collections
import unittest
import doctest
import sys

from test import support

from .pickletester import AbstractPickleTests
from .pickletester import AbstractPickleModuleTests
from .pickletester import AbstractPersistentPicklerTests
from .pickletester import AbstractPicklerUnpicklerObjectTests
from .pickletester import AbstractDispatchTableTests
from .pickletester import BigmemPickleTests
from .pickletester import AbstractBytestrTests
from .pickletester import AbstractBytesFallbackTests
from .pickletester import AbstractBytesAsStringTests

from zodbpickle import pickle

try:
    from zodbpickle import _pickle
except ImportError:
    has_c_implementation = False
else:
    has_c_implementation = True


class PickleTests(AbstractPickleModuleTests):
    pass


class PyPicklerBase(object):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    def dumps(self, arg, proto=None, **kwds):
        f = io.BytesIO()
        p = self.pickler(f, proto, **kwds)
        p.dump(arg)
        f.seek(0)
        return bytes(f.read())

    def loads(self, buf, **kwds):
        f = io.BytesIO(buf)
        u = self.unpickler(f, **kwds)
        return u.load()

class PyPicklerTests(PyPicklerBase, AbstractPickleTests):
    pass

class PyPicklerBytestrTests(PyPicklerBase, AbstractBytestrTests):
    pass

class PyPicklerBytesFallbackTests(PyPicklerBase, AbstractBytesFallbackTests):
    pass

class PyPicklerBytesAsStringTests(PyPicklerBase, AbstractBytesAsStringTests):
    pass

class InMemoryPickleTests(AbstractPickleTests, BigmemPickleTests):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    def dumps(self, arg, protocol=None):
        return pickle.dumps(arg, protocol)

    def loads(self, buf, **kwds):
        return pickle.loads(buf, **kwds)


class PyPersPicklerTests(AbstractPersistentPicklerTests):

    pickler = pickle._Pickler
    unpickler = pickle._Unpickler

    def dumps(self, arg, proto=None):
        class PersPickler(self.pickler):
            def persistent_id(subself, obj):
                return self.persistent_id(obj)
        f = io.BytesIO()
        p = PersPickler(f, proto)
        p.dump(arg)
        f.seek(0)
        return f.read()

    def loads(self, buf, **kwds):
        class PersUnpickler(self.unpickler):
            def persistent_load(subself, obj):
                return self.persistent_load(obj)
        f = io.BytesIO(buf)
        u = PersUnpickler(f, **kwds)
        return u.load()


class PyPicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests):

    pickler_class = pickle._Pickler
    unpickler_class = pickle._Unpickler


if sys.version_info >= (3, 3):
    class PyDispatchTableTests(AbstractDispatchTableTests):
        pickler_class = pickle._Pickler
        def get_dispatch_table(self):
            return pickle.dispatch_table.copy()


    class PyChainDispatchTableTests(AbstractDispatchTableTests):
        pickler_class = pickle._Pickler
        def get_dispatch_table(self):
            return collections.ChainMap({}, pickle.dispatch_table)


if has_c_implementation:
    class CPicklerTests(PyPicklerTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    class CPicklerBytestrTests(PyPicklerBytestrTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    class CPicklerBytesFallbackTests(PyPicklerBytesFallbackTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    class CPicklerBytesAsStringTests(PyPicklerBytesAsStringTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    class CPersPicklerTests(PyPersPicklerTests):
        pickler = _pickle.Pickler
        unpickler = _pickle.Unpickler

    class CDumpPickle_LoadPickle(PyPicklerTests):
        pickler = _pickle.Pickler
        unpickler = pickle._Unpickler

    class DumpPickle_CLoadPickle(PyPicklerTests):
        pickler = pickle._Pickler
        unpickler = _pickle.Unpickler

    class CPicklerUnpicklerObjectTests(AbstractPicklerUnpicklerObjectTests):
        pickler_class = _pickle.Pickler
        unpickler_class = _pickle.Unpickler

    if sys.version_info >= (3, 3):
        class CDispatchTableTests(AbstractDispatchTableTests):
            pickler_class = pickle.Pickler
            def get_dispatch_table(self):
                return pickle.dispatch_table.copy()

        class CChainDispatchTableTests(AbstractDispatchTableTests):
            pickler_class = pickle.Pickler
            def get_dispatch_table(self):
                return collections.ChainMap({}, pickle.dispatch_table)


def choose_tests():
    tests = [PickleTests, PyPicklerTests, PyPersPicklerTests,
             PyPicklerBytestrTests, PyPicklerBytesFallbackTests,
             PyPicklerBytesAsStringTests]
    if sys.version_info >= (3, 3):
        tests.extend([PyDispatchTableTests, PyChainDispatchTableTests])
    if has_c_implementation:
        tests.extend([CPicklerTests, CPersPicklerTests,
                      CPicklerBytestrTests, CPicklerBytesFallbackTests,
                      CPicklerBytesAsStringTests,
                      CDumpPickle_LoadPickle, DumpPickle_CLoadPickle,
                      PyPicklerUnpicklerObjectTests,
                      CPicklerUnpicklerObjectTests,
                      InMemoryPickleTests])
        if sys.version_info >= (3, 3):
            tests.extend([CDispatchTableTests, CChainDispatchTableTests])
    return tests

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(t) for t in choose_tests()
    ] + [
        doctest.DocTestSuite(pickle),
    ])

def test_main():
    tests = choose_tests()
    support.run_unittest(*tests)
    support.run_doctest(pickle)

if __name__ == "__main__":
    test_main()

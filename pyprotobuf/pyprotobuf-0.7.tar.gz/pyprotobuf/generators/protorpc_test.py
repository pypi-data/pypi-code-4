import unittest
from pyprotobuf.generators.protorpc import ProtoRPC
from pyprotobuf.main import parse_and_generate




class ProtorpcTest(unittest.TestCase):
    def check_expected_output(self, name):
        string = parse_and_generate(open('pyprotobuf/testdata/%s' % name).read(), 'test', ProtoRPC)
        self.assertMultiLineEqual(open('pyprotobuf/testdata/%s.py' % name).read(), string)

    def test_simple(self):
        """ Test simple evaluation
        """
        self.maxDiff = 1500
        self.check_expected_output('simple.proto')


    def test_enum(self):
        """ Test basic enum functionality.
        """
        self.maxDiff = 1500
        self.check_expected_output('enum.proto')

    def test_enum_global(self):
        """ Test enum globals are sorted.
        """
        self.maxDiff = 1500
        self.check_expected_output('enum_global.proto')


if __name__ == '__main__':
    unittest.main()

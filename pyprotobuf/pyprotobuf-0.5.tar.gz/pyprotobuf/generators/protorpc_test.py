import unittest
from pyprotobuf.generators.protorpc import ProtoRPC
from pyprotobuf.main import parse_and_generate


TEST_PROTO = """
option javascript_package = "com.example";
    
message Item {
  optional string aString = 1;
  optional int32 aNumber = 2;
  required string aRequiredString = 3;
  repeated string aRepeatedString = 4;
}
"""

TEST_MATCH = """################################################################################
# Automatically generated. Do not modify this file                             #
################################################################################
# test

from protorpc import messages


class Item(messages.Message):
    aString = messages.StringField(1)
    aNumber = messages.IntegerField(2)
    aRequiredString = messages.StringField(3, required=True)
    aRepeatedString = messages.StringField(4, repeated=True)


"""

class ProtorpcTest(unittest.TestCase):
    def test(self):
        TEST_STRING = '''
        
        '''
        self.maxDiff = 1000
        string = parse_and_generate(TEST_PROTO, 'test', ProtoRPC)
        self.assertMultiLineEqual(TEST_MATCH, string)


if __name__ == '__main__':
    unittest.main()

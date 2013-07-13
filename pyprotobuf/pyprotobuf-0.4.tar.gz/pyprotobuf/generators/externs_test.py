import unittest
from pyprotobuf.generators.externs import ClosureExterns
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

TEST_MATCH = """/* Automatically generated. Do not modify this file.
   test
*/


/** @constructor */
com.example.Item = function(){};

/** @type {string} */
com.example.Item.prototype.aString;

/** @type {number} */
com.example.Item.prototype.aNumber;

/** @type {string} */
com.example.Item.prototype.aRequiredString;

/** @type {[string]} */
com.example.Item.prototype.aRepeatedString;

"""

class ProtorpcTest(unittest.TestCase):
    def test(self):
        TEST_STRING = '''
        
        '''
        string = parse_and_generate(TEST_PROTO, 'test', ClosureExterns)
        self.assertMultiLineEqual(TEST_MATCH, string)


if __name__ == '__main__':
    unittest.main()

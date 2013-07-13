import unittest
import logging
import pyprotobuf.parser
import pyprotobuf.nodes
TOPLEVEL_TEST = '''
// file level comment
syntax = "proto2";
import "protobuf/js/javascript_package.proto";
option javascript_package = "proto2";
'''

MESSAGE_TEST = '''
/* Test message comment */
message TestAllTypes {
}
'''

MESSAGE_TEST1 = '''
message TestAllTypes {
// test field comment 1
optional    int32 optional_int32    =  1;
// test field comment 2
optional    int64 optional_int64    =  2 [default = 1];
optional    float optional_float    = 11 [default = 1.5];
optional    bytes optional_bytes    = 15 [default = "moo"];
optional int64 optional_int64_number =  50 [default = 1000000000000000001,
                                              (jstype) = JS_NUMBER];
repeated    int32 repeated_int32    =  31;
}
'''

ENUM_TEST = '''
enum NestedEnum {
    FOO = 0;
    BAR = 2;
    BAZ = 3;
}
'''


SERVICE_TEST = '''
// test comment
service SearchService {
  rpc Search (SearchRequest) returns (SearchResponse);
}
'''

class TestParser(unittest.TestCase):
    
    def test_toplevel(self):
        ''' Basic top level statements '''
        # test toplevel statements
        pp = pyprotobuf.parser.ProtoParser()
        protonode = pp.parse_string(TOPLEVEL_TEST)
        self.assertIsInstance(protonode.get_child(0), pyprotobuf.nodes.CommentNode)
        self.assertIsInstance(protonode.get_child(1), pyprotobuf.nodes.SyntaxNode)
        self.assertIsInstance(protonode.get_child(2), pyprotobuf.nodes.ImportNode)
        self.assertIsInstance(protonode.get_child(3), pyprotobuf.nodes.OptionNode)
    
    def test_message_decl(self):
        ''' Empty message decl. '''
        pp = pyprotobuf.parser.ProtoParser()
        protonode = pp.parse_string(MESSAGE_TEST)
        self.assertIsInstance(protonode.get_child(1), pyprotobuf.nodes.MessageNode)
        msg = protonode.get_child(1)
        self.assertEquals("TestAllTypes", msg.name)
        
    def test_basic_msg_decl(self):
        pp = pyprotobuf.parser.ProtoParser()
        protonode = pp.parse_string(MESSAGE_TEST1)
        msg = protonode.get_child(0)
        self.assertEquals("TestAllTypes", msg.name)
        self.assertEquals(8, len(msg.children))
        self.assertEquals('optional', msg.children[1].label)
        self.assertEquals(1, msg.children[1].number)
        self.assertEquals("1", msg.children[3].default)
        self.assertEquals("1.5", msg.children[4].default)
        self.assertEquals("moo", msg.children[5].default)
        self.assertEquals("repeated", msg.children[-1].label)
        self.assertEquals(31, msg.children[-1].number)
    
    def test_enum_decl(self):
        pp = pyprotobuf.parser.ProtoParser()
        protonode = pp.parse_string(ENUM_TEST)
        enum = protonode.get_child(0)
        self.assertIsInstance(protonode.get_child(0), pyprotobuf.nodes.EnumNode)
        
    def test_service_decl(self):
        pp = pyprotobuf.parser.ProtoParser()
        protonode = pp.parse_string(SERVICE_TEST)
        service = protonode.get_child(1)
        self.assertIsInstance(service, pyprotobuf.nodes.ServiceNode)
        self.assertEquals('SearchService', service.name)
        self.assertEquals('Search', service.children[0].name)
        self.assertEquals('SearchRequest', service.children[0].request_type)
        self.assertEquals('SearchResponse', service.children[0].response_type)
        
        
    def test_full(self):
        pp = pyprotobuf.parser.ProtoParser()
        protonode = pp.parse_string(open('pyprotobuf/tests/test.proto').read())
        message = protonode.get_child(11)
        
        logging.debug(protonode.children)
        
        self.assertIsInstance(message, pyprotobuf.nodes.MessageNode)
        self.assertEquals('TestAllTypes', message.name)
         
        
if __name__ == '__main__':
    unittest.main()
from pyprotobuf.compiler import Compiler
import pyprotobuf.nodes as nodes
import os
import unittest


class TestGenerator(object):
    def to_src(self, protonode):
        #out = [IMPORTS % protonode.filename + '\n\n']
        #out.append(self.visit(protonode))        
        #return ''.join(out)
        return ''


class CompilerTestCase(unittest.TestCase):
    def test_single_file_compile(self):
        c = Compiler(TestGenerator)

        root_node = c.precompile_string('pyprotobuf/tests/a.proto', open('pyprotobuf/tests/a.proto').read())

        self.assertIsInstance(root_node, nodes.RootNode)

        # XXX: we are actually testing the name resolver here

        self.assertEqual(2, len(root_node.children))

        # check the children are Package
        self.assertIsInstance(root_node.children[0], nodes.Package)
        self.assertIsInstance(root_node.children[1], nodes.Package)


        file_b = root_node.children[0].children[0]
        file_a = root_node.children[1].children[0]
        
        # check that imports resolve in the right order
        self.assertEquals('b.proto', os.path.basename(file_b.filename))
        self.assertEquals('a.proto', os.path.basename(file_a.filename))
        
        
        
        message_B = file_b.children[1]
        message_A = file_a.children[1]
        
        self.assertIsInstance(message_B, nodes.MessageNode)
        self.assertIsInstance(message_A, nodes.MessageNode)

        self.assertEquals(0, len(message_B.children))
        self.assertEquals(1, len(message_A.children))

        self.assertIsInstance(message_A.children[0].type, nodes.MessageNode)
        
        
        # check message A field's type resolves
        self.assertEqual(message_A.children[0].type, message_B)


if __name__ == '__main__':
    unittest.main()

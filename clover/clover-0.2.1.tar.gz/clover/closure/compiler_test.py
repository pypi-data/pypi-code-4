from __future__ import absolute_import
import unittest
from clover.closure.compiler import Compiler
from clover.sourcefiles.javascript import JavascriptSourceFile
from clover.config.cloverconfig import CloverConfig


class TestSource(JavascriptSourceFile):
    precompile = True

    def __init__(self, path, code):
        super(TestSource, self).__init__(path)
        self.__code = code

    def check_exists(self):
        return True

    def get_code_cached(self):
        return self.__code

class TestCompiler(unittest.TestCase):
    def test_compile(self):
        config = CloverConfig()
        config.data['mode'] = 'ADVANCED'

        TEST_SOURCE = '''\
function test(){
    alert("Test"); 
};
 
test();
'''
        sources = [TestSource('test.js', TEST_SOURCE)]
        
        compiler = Compiler()
        compiler.set_sources(sources)
        compiler.set_config(config)
        compilation = compiler.compile()
        self.assertEquals('alert("Test");', compilation.source)

    def test_compile_parse_error(self):
        config = CloverConfig()
        config.data['mode'] = 'ADVANCED'

        TEST_SOURCE_PARSE_ERROR = '''function test'''

        sources = [TestSource('test.js', TEST_SOURCE_PARSE_ERROR)]
        
        compiler = Compiler()
        compiler.set_sources(sources)
        compiler.set_config(config)
        
        compilation = compiler.compile()
        errors = compilation.errors
        self.assertEquals(1, len(errors))
        self.assertEquals(1, errors[0]['line'])
        self.assertEquals(12, errors[0]['column'])
        self.assertEquals('Parse error. missing ( before function parameters.', errors[0]['description'])
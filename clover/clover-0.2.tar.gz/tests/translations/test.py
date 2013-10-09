import unittest
import tempfile

import os

from clover.builder import Builder
from clover.config.yamlconfig import YamlConfig
from tests.seleniumtestcase import SeleniumTestCase


__dir__ = os.path.dirname(os.path.abspath(__file__))

TEST_TEMPLATE = '''<html>
<head><title>TEST</title></head>
<body><script src="file://%s"></script></body>
</html>'''

class Test(SeleniumTestCase):
    def test_translations(self):
        config = YamlConfig.from_file(os.path.join(__dir__, 'clover.yaml'))
        builder = Builder(config)
        compilation = builder.build()
        self.assertTrue(len(compilation.source) > 0)
        
        sourcefile = tempfile.NamedTemporaryFile('w', delete=False)
        sourcefile.write(compilation.source)
        sourcefile.close()
        
        htmlfile = tempfile.NamedTemporaryFile('w', delete=False)
        htmlfile.write(TEST_TEMPLATE % sourcefile.name)
        htmlfile.close()
        
        self.driver.get('file://%s' % htmlfile.name)
        
        # sanity check the html
        self.assertEqual("TEST", self.driver.title)

        self.assertEquals("Bonjour au monde!", self.driver.execute_script("return translation.getTestMessage();"))
        
        self.assertEquals("Bonjour, Testeur!", self.driver.find_element_by_id('output').text)


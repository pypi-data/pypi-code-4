from __future__ import absolute_import
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
    def test_simple_javascript_compilation(self):
        config = YamlConfig.from_file(os.path.join(__dir__, 'clover.yaml'))
        builder = Builder(config)
        compilation = builder.build()
        
        if True:
            self.assertIsNotNone(compilation.source)
            
            sourcefile = tempfile.NamedTemporaryFile('w', delete=False)
            sourcefile.write(compilation.source)
            sourcefile.close()
            
            htmlfile = tempfile.NamedTemporaryFile('w', delete=False)
            htmlfile.write(TEST_TEMPLATE % sourcefile.name )
            htmlfile.close()

            self.driver.get('file://%s' % htmlfile.name)
            
            # sanity check the html
            self.assertEqual("TEST", self.driver.title)
            
            self.assertEquals(True, self.driver.execute_script("return simple.main();"))
            # TODO: check adv compile by  checking for mising simple.*.


if __name__ == "__main__":
    unittest.main()
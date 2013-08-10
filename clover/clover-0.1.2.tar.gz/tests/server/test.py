from __future__ import absolute_import
import unittest
import os

from clover.config.yamlconfig import YamlConfig
from tests.seleniumtestcase import SeleniumTestCase

__dir__ = os.path.dirname(os.path.abspath(__file__))


TEST_TEMPLATE = '''<html>
<head><title>TEST</title></head>
<body><script src="file://%s"></script></body>
</html>'''

from clover.config.multiconfig import MultiDocConfig
from clover.server.main import Server
import multiprocessing

CONFIG_FILE = os.path.join(__dir__, 'clover.yaml')

import sys
import time
import atexit

class ServerProcess(multiprocessing.Process):
    started_event = multiprocessing.Event()
    def __init__(self):
        super(ServerProcess, self).__init__()
        
    def run(self):
        
        mdc = MultiDocConfig(CONFIG_FILE)
        
        config = YamlConfig.from_file(CONFIG_FILE)
        mdc.add_config(config)
        
        s = Server(mdc)
        
        print >> sys.stderr, "STARTING"
        
        s.start()
        
        #self.started_event.set()
        
        print >> sys.stderr, "STARTED"
        
        

class Test(SeleniumTestCase):
    
    def setUp(self):
        super(Test, self).setUp()
        
        self.proc = ServerProcess()
        self.proc.start()
        atexit.register(self.proc.terminate)
        time.sleep(3)

        #self.proc.started_event.wait()
        #self.driver.get('http://localhost:2323')3
        
    def tearDown(self):
        super(Test, self).tearDown()
        self.proc.terminate()
        time.sleep(2)
        
    def test_test_runner(self):
        
        #self.driver.get('http://localhost:2323')
        #self.assertEquals("Bonjour au monde!", self.driver.execute_script("return translation.getTestMessage();"))
        
        self.driver.get('http://localhost:2323/configs/server/test?path=main_test.js')
        self.assertEquals("The meaning of life is: 42.", self.driver.find_element_by_id('output').text)
        
        
        
        
        
        
        #builder = Builder(config)
        #compilation = builder.build()
#
        #
        #
        ## check if the output is usable
        #
        #
        ## check if the test pages render
        #
        #
        #if True:
        #    self.assertIsNotNone(compilation.source)
#
        #    sourcefile = tempfile.NamedTemporaryFile('w', delete=False)
        #    sourcefile.write(compilation.source)
        #    sourcefile.close()
#
        #    htmlfile = tempfile.NamedTemporaryFile('w', delete=False)
        #    htmlfile.write(TEST_TEMPLATE % sourcefile.name)
        #    htmlfile.close()
#
        #    self.driver.get('file://%s' % htmlfile.name)
#
        #    # sanity check the html
        #    self.assertEqual("TEST", self.driver.title)
#
        #    self.assertEquals(True, self.driver.execute_script("return server.main();"))
        #    
        #    
        #    
        #    
        #    # TODO: check adv compile by  checking for mising simple.*.


if __name__ == "__main__":
    unittest.main()
__author__ = 'yarnaid'

import unittest
import test.test_pixelmap as test_pixelmap
import test.test_properties as test_properties
import tools.test.test_convertation as test_convertation
import tools.test.test_tools as test_tools


loader = unittest.TestLoader()

suite_glespy = loader.loadTestsFromModule(test_pixelmap)
suite_glespy.addTest(loader.loadTestsFromModule(test_properties))

suite_tools = loader.loadTestsFromModule(test_convertation)
suite_tools = loader.loadTestsFromModule(test_tools)

runner = unittest.TextTestRunner()
# runner.run(suite_tools)
# runner.run(suite_glespy)

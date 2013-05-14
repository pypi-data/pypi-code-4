import unittest

from smssluzbacz_api.test import test_lite_api, test_post_api


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromModule(test_lite_api))
    suite.addTest(loader.loadTestsFromModule(test_post_api))
    unittest.TextTestRunner(verbosity=2).run(suite)
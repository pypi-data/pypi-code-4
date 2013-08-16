import unittest

from Products.PloneTestCase.layer import PloneSite as PloneLayer
from kreagroup.jsi18n.tests.base import KreaGroupJSi18nPloneTestCase


PRODUCT_NAMES = ('kreagroup.jsi18n', 'jarn.jsi18n',)

class Layer(PloneLayer):
    pass

class TestSetup(KreaGroupJSi18nPloneTestCase):

    layer = Layer


    def test_kreagroup_jsi18n_installation_and_dependencies(self):
        for product_name in PRODUCT_NAMES:
            self.check_product_available_and_installed(product_name)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

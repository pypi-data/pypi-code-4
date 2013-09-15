import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from raptus.article.addthis.testing import\
    RAPTUS_ARTICLE_ADDTHIS_INTEGRATION


class TestExample(unittest.TestCase):

    layer = RAPTUS_ARTICLE_ADDTHIS_INTEGRATION
    
    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
    
    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product 
            installed
        """
        pid = 'raptus.article.addthis'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

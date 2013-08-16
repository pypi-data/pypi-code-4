from Products.CMFCore.utils import getToolByName
from kreagroup.policy.helper import test

MY_PACKAGE_NAME = 'kreagroup.jsi18n'

test.setup_my_package_for_plone(MY_PACKAGE_NAME)


class KreaGroupJSi18nPloneTestCase(test.KreaGroupPloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
    def uninstall_package(self):
        portal_quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        portal_quickinstaller.uninstallProducts(products=[MY_PACKAGE_NAME])

class KreaGroupJSi18nSeleniumTestCase(test.KreaGroupSeleniumTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
    def uninstall_package(self):
        portal_quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        portal_quickinstaller.uninstallProducts(products=[MY_PACKAGE_NAME])

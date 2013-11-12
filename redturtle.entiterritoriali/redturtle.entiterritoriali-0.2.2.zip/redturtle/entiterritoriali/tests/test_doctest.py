import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing
from Products.Five import fiveconfigure, zcml

def setUp(site):
    """
    setup method for test instance
    """
    testing.setUp(site)
    fiveconfigure.debug_mode = True
    import redturtle.entiterritoriali
    import Products.Five
    import Products.GenericSetup
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('meta.zcml', Products.GenericSetup)
    zcml.load_config('configure.zcml', Products.Five)
    zcml.load_config('configure.zcml', redturtle.entiterritoriali)
    fiveconfigure.debug_mode = False


def test_suite():
    return unittest.TestSuite([

        # Unit tests for your API
        doctestunit.DocFileSuite(
            'README.txt', package='redturtle.entiterritoriali',
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            setUp=setUp, tearDown=testing.tearDown),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

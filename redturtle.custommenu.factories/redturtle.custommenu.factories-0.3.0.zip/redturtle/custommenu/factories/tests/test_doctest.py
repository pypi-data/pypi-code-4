import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing, eventtesting, provideAdapter

from Testing import ZopeTestCase as ztc

from redturtle.custommenu.factories.tests import base

def setUp(test):
    """This method is used to set up the test environment. We pass it to the
    DocFileSuite initialiser. We also pass a tear-down, but in this case,
    we use the tear-down from zope.component.testing, which takes care of
    cleaning up Component Architecture registrations.
    """
    
    # Register the adapter. See zope.component.interfaces for more

    from redturtle.custommenu.factories.tests.adapters import SpecialFolderFactoryMenuAdapter
    provideAdapter(SpecialFolderFactoryMenuAdapter)


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.ZopeDocFileSuite(
            'README.txt', package='redturtle.custommenu.factories',
            test_class=base.FunctionalTestCase,
            setUp=setUp,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

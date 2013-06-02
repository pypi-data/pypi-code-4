import unittest
from zope.testing import doctest
from zope.component import testing
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup, PloneSite
from Products.Five import zcml

@onsetup
def load_zcml():
    import p4a.subtyper
    zcml.load_config('configure.zcml', p4a.subtyper)

load_zcml()
PloneTestCase.setupPloneSite()

def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS

    unitsuite = unittest.TestSuite((
        doctest.DocFileSuite('subtyping.txt',
                             setUp=testing.setUp,
                             tearDown=testing.tearDown,
                             optionflags=flags),
        ))

    fsuite = unittest.TestSuite((
        FunctionalDocFileSuite('browser.txt',
                               package='p4a.subtyper',
                               optionflags=flags,
                               test_class=PloneTestCase.FunctionalTestCase),
        ))
    fsuite.layer = PloneSite

    return unittest.TestSuite((unitsuite, fsuite))

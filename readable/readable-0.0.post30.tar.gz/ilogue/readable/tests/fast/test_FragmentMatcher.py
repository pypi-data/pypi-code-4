import unittest
from mock import Mock
from ilogue.readable import assertionMethod, assertMethod, setupMethod
from ilogue.readable.matching import that



class FragmentMatcherTestCase(unittest.TestCase):

    def test_Can_check_for_property_by_name(self):
        from ilogue.readable.FragmentMatcher import FragmentMatcher
        #self.fail()

    def test_Checks_property_value(self):
        from ilogue.readable.FragmentMatcher import FragmentMatcher
#        frg = ''
#        fragment = FragmentMatcher(frg)
#        (assertionMethod(fragment.withPropertyAndValue)
#            .withPrecedingArgument('propname')
#            .doesNotFailIfPassedMatchingMatcher()
#            .failsWithAppropriateMessageIfPassedNonMatchingMatcher())

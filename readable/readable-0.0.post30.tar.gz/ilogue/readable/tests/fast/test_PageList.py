import unittest
from mock import Mock
from ilogue.readable import assertionMethod, assertMethod, setupMethod
from ilogue.readable.matching import that



class PageListTestCase(unittest.TestCase):

    def test_withLength_asserts_number_of_items_in_list(self):
        from ilogue.readable.PageList import PageList
        listWithThreeItems = '<ul><html:li>sth</l1><html:li>sth</l1><html:li>sth</l1></ul>'
        myList = PageList(listWithThreeItems)
        (assertionMethod(myList.withLength)
            .doesNotFailIfPassed(3)
            .failsIfPassed(4))

    def test_withAnItem_tests_matcher_on_each_item(self):
        from ilogue.readable.PageList import PageList
        listWithThreeItems = '<ul><html:li>one</l1><html:li>two</l1><html:li>three</l1></ul>'
        myList = PageList(listWithThreeItems)
        (assertionMethod(myList.withAnItem)
            .doesNotFailIfPassedMatchingMatcher()
            .failsWithAppropriateMessageIfPassedNonMatchingMatcher())
        myList = PageList(listWithThreeItems)
        itemMatcher = self.failingMatcher()
        try:
            myList.withAnItem( itemMatcher )
        except:
            pass
        (assertMethod(itemMatcher.matches).wasCalled().once()
            .withArgument( that().isString().containing('one') ))
        (assertMethod(itemMatcher.matches).wasCalled().once()
            .withArgument( that().isString().containing('two') ))
        (assertMethod(itemMatcher.matches).wasCalled().once()
            .withArgument( that().isString().containing('three') ))

    def failingMatcher(self):
        from ilogue.readable.matcher import Matcher
        itemMatcher = Matcher()
        itemMatcher.matchFor = Mock()
        itemMatcher.matches = Mock()
        setupMethod(itemMatcher.matches).toReturn(False)
        return itemMatcher

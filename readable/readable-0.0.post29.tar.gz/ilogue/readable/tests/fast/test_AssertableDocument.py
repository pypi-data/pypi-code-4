#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock, sentinel
from ilogue.readable import assertionMethod, assertMethod, setupMethod
from ilogue.readable.assertableassertion import MatcherMock

class AssertableRequestTestCase(unittest.TestCase):

    def test_hasLink(self):
        from ilogue.readable.AssertableDocument import AssertableDocument
        doc = AssertableDocument('<a href="http://somewh.ere">existing link name</a>')
        (assertionMethod(doc.hasLink)
            .failsIfPassed('nonexisting name')
            .doesNotFailIfPassed('existing link name'))

    def test_hasA_matcher_appropriate(self):
        from ilogue.readable.AssertableDocument import AssertableDocument
        doc = AssertableDocument('<html><form></form></html>')
        (assertionMethod(doc.hasA)
            .failsWithAppropriateMessageIfPassedNonMatchingMatcher()
            .doesNotFailIfPassedMatchingMatcher())

    def test_hasA_if_passed_formmatcher_will_try_match_all_form_elements(self):
        from ilogue.readable.AssertableDocument import AssertableDocument
        doc = AssertableDocument('<html><form><c>1</c></form>'+
            '<div><form><c>2</c></form></div></html>')
        matcher = MatcherMock().willNotMatch()
        try:
            doc.hasA(matcher)
        except AssertionError:
            pass
        (assertMethod(matcher.matchFor).wasCalled()
            .once().withArgument('<form><c>1</c></form>')
            .once().withArgument('<form><c>2</c></form>'))

    def test_hasA_returns_matched_matchers_interaction(self):
        from ilogue.readable.AssertableDocument import AssertableDocument
        from ilogue.readable import FormInteraction
        doc = AssertableDocument('<html><form></form></html>')
        matcher = MatcherMock().willMatch()
        returned = doc.hasA(matcher)
        assert isinstance(returned, FormInteraction)

    def test_containsText_True_if_string_in_doc_somewhere(self):
        from ilogue.readable.AssertableDocument import AssertableDocument
        doc = AssertableDocument('<div>something here<p>target text</p></div>')
        (assertionMethod(doc.containsText)
            .failsIfPassed('something else')
            .doesNotFailIfPassed('target text'))
        


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

# tests for the machines class

import unittest
from mock import Mock
from ilogue.readable import assertionMethod


#TODO: more loose-coupled AssertablePageView,
# add method to Matcher, assertMatches()
class AssertableResponseTestCase(unittest.TestCase):

    def test_WithPropertyAndValue_should_use_passed_matcher(self):
        from ilogue.readable.assertableresponse import PageSection
        section = PageSection(Mock())
        section.findProperty = Mock()
        section.propertyValue = Mock()
        (assertionMethod(section.WithPropertyAndValue)
            .withPrecedingArgument('AProperty')
            .doesNotFailIfPassedMatchingMatcher()
            .failsWithAppropriateMessageIfPassedNonMatchingMatcher())

    def test_Accepts_page_as_string(self):
        from ilogue.readable.assertableresponse import AssertableResponse
        view = AssertableResponse(None, content = "<root/>")
        assert view

    def test_If_based_on_string_should_create_FormMatcher_with_testappBased_False(self):
        from ilogue.readable.assertableresponse import AssertableResponse
        view = AssertableResponse(None, content = "<root><form></form></root>")
        assert view.hasForm().isTestappBased == False

    def test_fails_for_hasList_if_page_does_not_contain_a_ul(self):
        from ilogue.readable.assertableresponse import AssertableResponse
        responseWithoutList = AssertableResponse(None, content = "<root></root>")
        responseWithList = AssertableResponse(None, content = "<root><ul></ul></root>")
        self.assertRaises(AssertionError,responseWithoutList.hasList)
        assert responseWithList.hasList()

    def test_containsTextSomewhere_matches_text_anywhere_in_body(self):
        from ilogue.readable.assertableresponse import AssertableResponse
        response = AssertableResponse(None, content = "<root>ThisText</root>")
        (assertionMethod(response.containsTextSomewhere)
            .doesNotFailIfPassed('ThisText')
            .failsIfPassed('OtherText'))


if __name__ == '__main__':
    unittest.main()

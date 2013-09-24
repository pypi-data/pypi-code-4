#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

from mock import Mock
from ilogue.readable.matcher import Matcher


class AssertableAssertion():
    withFirstArg = False
    firstArgValue = None

    def __init__(self, assertionMethod):
        self.method = assertionMethod

    def withPrecedingArgument(self, argValue):
        self.withFirstArg = True
        self.firstArg = argValue
        return self

    def doesNotFailIfPassedMatchingMatcher(self):
        failure = self.tryCallWithMatcher(
            MatcherMock().willMatch())
        if failure:
            raise AssertionError(
                "Assertion method with matching Matcher" +
                " passed threw AssertionError."+str(failure))
        return self

    def fails(self):
        failure = self.tryCall()
        if not failure:
            raise AssertionError(
                "Assertion method did not throw AssertionError.")
        return self

    def failsWithAppropriateMessageIfPassedNonMatchingMatcher(self):
        matcher = MatcherMock().willNotMatch()
        failure = self.tryCallWithMatcher(matcher)
        if not failure:
            raise AssertionError(
                "Assertion method with non-matching Matcher" +
                " passed did not throw AssertionError.")
        if not (matcher.matchMessage in str(failure) or 
                str(matcher) in str(failure)):
            raise AssertionError(
                ("Assertion method with non-matching Matcher" +
                " threw AssertionError with message '{0}'," +
                " but should at least contain '{1}' or '{2}'")
                .format(str(failure), matcher.matchMessage, str(matcher)))
        return self

    def doesNotFail(self):
        failure = self.tryCall()
        if failure:
            raise AssertionError(
                "Assertion method threw AssertionError unexpectedly."+str(failure))
        return self

    def doesNotFailIfPassed(self,toMatch):
        failure = self.tryCall(toMatch)
        if failure:
            raise AssertionError(
                "Assertion method threw AssertionError unexpectedly."+str(failure))
        return self

    def failsIfPassed(self,toMatch):
        matcher = MatcherMock().willNotMatch()
        failure = self.tryCall(toMatch)
        if not failure:
            raise AssertionError(
                "Assertion method did not throw AssertionError.")
        return self

    def tryCallWithMatcher(self, matcher):
        failure = None
        try:
            if self.withFirstArg:
                self.method(self.firstArgValue, matcher)
            else:
                self.method(matcher)
        except AssertionError as err:
            failure = err
        return failure

    def tryCall(self, toMatch=None):
        failure = None
        try:
            if toMatch is None:
                self.method()
            elif self.withFirstArg:
                self.method(self.firstArgValue, toMatch)
            else:
                self.method(toMatch)
        except AssertionError as err:
            failure = err
        return failure

class MatcherMock(Matcher):

    def __init__(self):
        super(MatcherMock, self).__init__()
        self.matchFor = Mock()

    def willMatch(self):
        self.matchFor.return_value = MatchMock()
        return self

    def willNotMatch(self):
        self.matchFor.return_value = MismatchMock()
        return self

    @property
    def matchMessage(self):
        return str(self.matchFor())


class MatchMock():
    successful = True

    def __str__(self):
        return "Mocked Match"


class MismatchMock():
    successful = False

    def __str__(self):
        return "Mocked Mismatch"

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

# wrapper for pymock

from ilogue.readable.callmatch import CallMatch as Match
from ilogue.readable.matcher import Matcher


class AssertableMethod(object):
    def __init__(self, mockMethod):
        self.__inner = mockMethod
        # setup method call matches to just match last call:
        self.sequenceState = 'lastCall'

    def wasCalled(self):
        assert self.__inner.called, "Mocked method wasn't called."
        return self

    def wasNotCalled(self):
        assert self.__inner.called == False, "Mocked method was called."

    def once(self):
        # sets up a check for arguments that should match one of many calls
        self.sequenceState = 'once'
        return self

    def exactlyOnce(self):
        assert self.__inner.call_count == 1, ("Mocked method wasn't called "
            "exactly once, but {0} times.".format(self.__inner.call_count))
        return self

    def withArgument(self, argument):
        return self.withArguments(argument)

    def withArguments(self, *expOrderedArgs, **expKeywordArgs):
        if self.sequenceState == 'lastCall':
            actualArgs = self.__inner.call_args
            match = self.matchArgsToCallArgs(expOrderedArgs,
                expKeywordArgs, actualArgs)
            if not match.successful:
                raise AssertionError(str(match))
        elif self.sequenceState == 'once':
            failedMatches = []
            for callArgs in self.__inner.call_args_list:
                match = self.matchArgsToCallArgs(expOrderedArgs,
                    expKeywordArgs, callArgs)
                if match.successful:
                    break
                else:
                    failedMatches.append(match)
            else:
                raise AssertionError(("No method call matched. failures: {0}".
                        format([str(m) for m in failedMatches])))
        else:
            raise NotImplementedError("Unknown RedableMock sequenceState.")
        self.sequenceState = 'lastCall'
        return self

    def matchArgsToCallArgs(self, expOrderedArgs, expKeywordArgs, actualArgs):
        actualOrderedArgs = actualArgs[0]
        for argIndex, expArg in enumerate(expOrderedArgs):
            if not argIndex < len(actualOrderedArgs):
                return Match.MissingArgument(argIndex, expArg)
            actArg = actualOrderedArgs[argIndex]
            if self.isMatcher(expArg):
                if not expArg.matches(actArg):
                    return expArg.matchFor(actArg)
            elif not expArg == actArg:
                return Match.WrongArgument(argIndex, actArg, expArg)
        actualKeywordArgs = actualArgs[1]
        for argKey, expArg in expKeywordArgs.items():
            if not argKey in actualKeywordArgs:
                return Match.MissingArgument(argKey, expArg)
            actArg = actualKeywordArgs[argKey]
            if self.isMatcher(expArg):
                if not expArg.matches(actArg):
                    return expArg.matchFor(actArg)
            elif not expArg == actArg:
                return Match.WrongArgument(argKey, actArg, expArg)
        return Match()

    def isMatcher(self, matcherCandidate):
        return isinstance(matcherCandidate, Matcher)

if __name__ == '__main__':
    print(__doc__)

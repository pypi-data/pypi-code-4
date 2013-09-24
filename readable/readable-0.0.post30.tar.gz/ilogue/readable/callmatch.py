#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>


class CallMatch(object):
    MISSARG_MSG = "Missing argument: [{indexOrKey}] ({exp})."
    ARGMISMATCH_MSG = "Arg [{indexOrKey}] ({act}) is not as expected ({exp})."
    SUCCESS_MSG = "Successful match."

    @classmethod
    def MissingArgument(cls, indexOrKey, expectedArg):
        return cls(False, "missing", indexOrKey, expectedArg)

    @classmethod
    def WrongArgument(cls, indexOrKey, actualArg, expectedArg):
        return cls(False, "wrong", indexOrKey, expectedArg, actualArg)

    def __init__(self, success=True,
                    failType="success",
                    indexOrKey=None,
                    expectedArg=None,
                    actualArg=None):
        self.__success = success
        self.__indexOrKey = indexOrKey
        self.__expectedArg = expectedArg
        self.__actualArg = actualArg
        self.__failType = failType

    @property
    def successful(self):
        return self.__success

    def __str__(self):
        if self.__failType == "missing":
            return self.MISSARG_MSG.format(indexOrKey=self.__indexOrKey,
                                    exp=self.__expectedArg)
        elif self.__failType == "wrong":
            return self.ARGMISMATCH_MSG.format(indexOrKey=self.__indexOrKey,
                                    exp=self.__expectedArg,
                                    act=self.__actualArg)
        elif self.__failType == "success":
            return self.SUCCESS_MSG
        else:
            raise NotImplementedError("Unknown Match failType.")

if __name__ == '__main__':
    print(__doc__)

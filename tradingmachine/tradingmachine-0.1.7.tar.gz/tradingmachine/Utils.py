'''
Copyright 2013-2013 Chen Huang.
All rights reserved. FreeBSD License.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the
     distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from tradingmachine.sharedLogger import logger
import os
from tradingmachine import Error
import configparser
from os.path import expanduser
# import types as tp

# HISTORICALDATABASEPATH = os.path.join(os.path.dirname(__file__), "DataFeed", "historicaldata")
config = configparser.ConfigParser()
config.read(os.path.join(expanduser("~"), ".tmconfig.ini"))
HISTORICALDATABASEPATH = os.path.join(config["DEFAULT"]["HistoricalDataPath"])
logger.info("Historical Data Path is {}.".format(HISTORICALDATABASEPATH))
RAWDATAFOLDER = "RawData"
FORMATTEDDATAFOLDER = "FormattedData"
SAMPLESFOLDER = "samples"


def accepts(*types, **kwtypes):
    """
    Semi-static Typing
    """
    def wrapper(func):
        def call(*args, **kwargs):
            for index, arg in enumerate(args):
                # TODO: This static typing checks for function. That means instance methods need to specify "self" type,
                # which is unnecessary. We should improve this semi-static typing that bypass "self"
                # print(type(func))
                # if (isinstance(type(func), tp.MethodType) and index == 0):
                #     # ignore the first parameter "self"
                #     continue
                if not isinstance(arg, types[index]):
                    raise Error.TypeMismatchError("Positional Parameter at index {} should be type of {}. {} is provided.".format(
                        index, types[index], type(arg)))
            for index, arg in enumerate(kwargs):
                if arg in kwtypes:
                    if not isinstance(kwargs[arg], kwtypes[arg]):
                        raise Error.TypeMismatchError("Keyword Parameter {} should be type of {}. {} is provided.".format(
                            arg, types[index], type(kwargs[arg])))
                else:
                    raise Error.UnknownKeywordArgumentError("Unknown keyword Parameter {} is provided.".format(arg))
            return func(*args, **kwargs)
        return call
    return wrapper


def returns(returnType):
    def wrapper(func):
        def call(*args, **kwargs):
            result = func(*args, **kwargs)
            if not isinstance(result, returnType):
                raise Error.TypeMismatchError("Return type of {} should be type of {}. {} is returned.".format(
                    func.__qualname__, returnType, type(result)))
            return result
        return call
    return wrapper


class Enum(object):

    """
    A class that is useful for dealing with C-style enums. Maps constants (defined as Enum objects) onto integer values while providing descriptions.
    Use Enum.valueMap[int] to reverse map a C style enum value back to the python constant.

    Make sure to override valueMap when subclassing.
    """
    valueMap = {}

    def __init__(self, value, description):
        self.value = value
        self.description = description
        self.valueMap[value] = self

    def __int__(self):
        return self.value

    def __repr__(self):
        return self.description

    def __str__(self):
        return self.description


class Utils(object):

    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
    @classmethod
    def LoadData(filePath=None):
        logger.info("Loading file %s.", filePath)
        if(filePath):
            pass
        else:
            return -1

#
# Jasy - Web Tooling Framework
# Copyright 2010-2012 Zynga Inc.
#

import re, os, hashlib, tempfile, subprocess, sys, shlex

import jasy.core.Console as Console


def executeCommand(args, failMessage=None, path=None, wrapOutput=True):
    """
    Executes the given process and outputs failMessage when errors happen.

    :param args: 
    :type args: str or list
    :param failMessage: Message for exception when command fails
    :type failMessage: str
    :param path: Directory path where the command should be executed
    :type path: str
    :raise Exception: Raises an exception whenever the shell command fails in execution
    :type wrapOutput: bool
    :param wrapOutput: Whether shell output should be wrapped and returned (and passed through to Console.debug())
    """

    if type(args) == str:
        args = shlex.split(args)

    prevpath = os.getcwd()

    # Execute in custom directory
    if path:
        path = os.path.abspath(os.path.expanduser(path))
        os.chdir(path)

    Console.debug("Executing command: %s", " ".join(args))
    Console.indent()
    
    # Using shell on Windows to resolve binaries like "git"
    if not wrapOutput:
        returnValue = subprocess.call(args, shell=sys.platform == "win32")
        result = returnValue

    else:
        output = tempfile.TemporaryFile(mode="w+t")
        returnValue = subprocess.call(args, stdout=output, stderr=output, shell=sys.platform == "win32")
            
        output.seek(0)
        result = output.read().strip("\n\r")
        output.close()

    # Change back to previous path
    os.chdir(prevpath)

    if returnValue != 0 and failMessage:
        raise Exception("Error during executing shell command: %s (%s)" % (failMessage, result))
    
    if wrapOutput:
        for line in result.splitlines():
            Console.debug(line)
    
    Console.outdent()
    
    return result


def getKey(data, key, default=None):
    """
    Returns the key from the data if available or the given default

    :param data: Data structure to inspect
    :type data: dict
    :param key: Key to lookup in dictionary
    :type key: str
    :param default: Default value to return when key is not set
    :type default: any
    """

    if key in data:
        return data[key]
    else:
        return default


__REGEXP_DASHES = re.compile(r"\-+([\S]+)?")
__REGEXP_HYPHENATE = re.compile(r"([A-Z])")

def __camelizeHelper(match):
    result = match.group(1)
    return result[0].upper() + result[1:].lower()

def __hyphenateHelper(match):
    return "-%s" % match.group(1).lower()
    
def camelize(str):
    """
    Returns a camelized version of the incoming string: foo-bar-baz => fooBarBaz

    :param str: Input string
    """
    return __REGEXP_DASHES.sub(__camelizeHelper, str)

def hyphenate(str):
    """Returns a hyphenated version of the incoming string: fooBarBaz => foo-bar-baz

    :param str: Input string
    """

    return __REGEXP_HYPHENATE.sub(__hyphenateHelper, str)    


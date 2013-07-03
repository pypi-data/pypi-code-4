""" The module is dedicated to utils """

import ast
import pickle
import json
import logging


logger = logging.getLogger(__name__)


def load(fileobj):
    """ It tries to get data from the storage. """
    for loader in (json.load, pickle.load):
        fileobj.seek(0)
        try:
            return loader(fileobj)
        except:
            pass
    raise ValueError('File is not in the supported format.')


def str_to_pyobject(string):
    """ It converts a string into a python object """
    result = string
    try:
        result = ast.literal_eval(string)
        logger.info("The string '%s' was converted." % string)
    except (ValueError, SyntaxError):
        logger.info("Can't convert the string: '%s'" % string)
    return result


def dict_to_pyobject(dictionary):
    """ It converts a dictionary into a python object """
    return dict((key, str_to_pyobject(value)) for key, value in dictionary.iteritems())

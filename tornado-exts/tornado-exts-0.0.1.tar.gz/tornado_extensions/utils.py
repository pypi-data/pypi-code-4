import os
import fnmatch
import re


def check_callable(fun, required=False):
    if required and not fun:
        raise TypeError("callable is required")
    if fun is not None and not callable(fun):
        raise TypeError("callback must be callable")


def file_filter(path='./', patterns=['*']):
    r"""Filters files in directory with specified patterns
        Example
        -------
        file_filter('./', ["json", "xml"])
    """
    if not isinstance(patterns, list):
        patterns = [patterns]
    matching_rule = '|'.join([pat for pat in patterns])
    res = []
    for (dirpath, dirname, fnames) in os.walk(path):
        res = fnmatch.filter(fnames, matching_rule)
    return [os.path.join(path, f) for f in res]

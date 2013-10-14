#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A data loader utilities

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
from graf.config import settings
from graf.parser import BaseParser
from graf.loader import BaseLoader
from graf.plugins import registry

"""default parser instance (private)"""
_parser = None
"""default loader instance (private)"""
_loader = None


def load(pathname, using=None, unite=False, basecolumn=0,
         parser=None, loader=None, **kwargs):
    """
    Load data from file matched with given glob pattern

    Return value will be a list of data unless `unite` is true.
    If `unite` is true then all data will be united into a single data.

    Args:
        pathname: a glob pattern
        using: a list of index or slice instance
        unite: if it is true, returning dataset will be united into a single
            data
        basecolumn: an index of base column. all data will be trimmed based on
            the order of this column when the number of samples are different
            among the dataset (Default: 0). It only affect when `unite` is
            true
        parser: an instance or registered name of parser class.
            if it is not specified, default parser specified in configuration
            file will be used.
        loader: an instance or registered name of loader class
            if it is not specified, default loader specified in configuration
            file will be used.
        **kwargs: optional arguments

    Returns:
        A list of numpy array or A nested list of numpy array
    """
    parser = parser or get_default_parser()
    loader = loader or get_default_loader()
    dataset = loader.glob(pathname,
            using=using, parser=parser,
            unite=unite, basecolumn=basecolumn,
            **kwargs)
    return dataset

def get_default_parser():
    """
    Get default parser instance

    Returns:
        an instance of parser class
    """
    if _parser is None:
        parser_name = settings['default']['parser']
        set_default_parser(parser_name)
    return _parser

def set_default_parser(parser):
    """
    Set defaulr parser instance

    Args:
        parser: an instance or registered name of parser class
    """
    if isinstance(parser, basestring):
        parser = registry.find(parser)()
    if not isinstance(parser, BaseParser):
        parser = parser()
    global _parser
    _parser = parser

def get_default_loader():
    """
    Get default loader instance

    Returns:
        an instance of loader class
    """
    if _loader is None:
        loader_name = settings['default']['loader']
        set_default_loader(loader_name)
    return _loader

def set_default_loader(loader):
    """
    Set defaulr loader instance

    Args:
        parser: an instance or registered name of loader class
    """
    if isinstance(loader, basestring):
        loader = registry.find(loader)()
    if not isinstance(loader, BaseLoader):
        loader = loader()
    global _loader
    _loader = loader

def __plugin__(registry):
    registry.register('load', load)
    registry.register('get_default_parser', get_default_parser)
    registry.register('set_default_parser', set_default_parser)
    registry.register('get_default_loader', get_default_loader)
    registry.register('set_default_loader', set_default_loader)
__plugin__.manually = True

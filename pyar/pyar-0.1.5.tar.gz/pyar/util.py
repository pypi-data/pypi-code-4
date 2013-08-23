#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

import sys

if sys.version_info < (2, 6):
    # emits a nasty deprecation warning
    # in newer pythons
    from cgi import parse_qsl
else:
    from urlparse import parse_qsl

import logging

def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
    
class PluginLoader(object):

    def __init__(self, group, auto_fn=None):
        self.group = group
        self.impls = {}
        self.auto_fn = auto_fn

    def load(self, name):
        if name in self.impls:
            return self.impls[name]()

        if self.auto_fn:
            loader = self.auto_fn(name)
            if loader:
                self.impls[name] = loader
                return loader()

        try:
            import pkg_resources
        except ImportError:
            pass
        else:
            for impl in pkg_resources.iter_entry_points(
                                self.group, name):
                self.impls[name] = impl.load
                return impl.load()

        from . import exc
        raise exc.ArgumentError(
                "Can't load plugin: %s:%s" %
                (self.group, name))

    def register(self, name, modulepath, objname):
        def load():
            mod = __import__(modulepath)
            for token in modulepath.split(".")[1:]:
                mod = getattr(mod, token)
            return getattr(mod, objname)
        self.impls[name] = load

from twisted import plugin

from csat import collectors
from csat.acquisition import base


def get_collector(key):
    for c in get_collectors():
        if key == c.key:
            return c


def get_collectors():
    return plugin.getPlugins(base.ICollectorConfigurator, collectors)


def get_factories():
    return plugin.getPlugins(base.ICollectorFactory, collectors)


def get_django_applications():
    for collector in get_collectors():
        yield collector.__class__.__module__

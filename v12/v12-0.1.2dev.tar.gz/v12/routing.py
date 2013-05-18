import os
from utils import *


class URLRoute(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, f):
        self.kwargs['handler'] = f.__module__ + "." + f.__name__
        RouteManifest.add({'args': self.args, 'kwargs': self.kwargs})
        return f


class MetaRouteManifest(MetaDataFileUtil):
    _persisted_data = []

    @property
    def _DATA_FILE(cls):
        return os.path.join(env.project_path, "config/routes.json")

    def get_route_list(cls):
        cls._load()
        return cls._persisted_data

    @persisted_data_modifier
    def add(cls, route):
        cls._persisted_data.append(route)

class RouteManifest(object): __metaclass__ = MetaRouteManifest
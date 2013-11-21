import threading

from pkg_resources import iter_entry_points
import pymongo

from .managers import NodeManager, ActivityManager, Aggregator
from .storage import pymongostorage

_director = None


class ActivityDirector(threading.local):
    def __init__(self, **conf):
        self.conf = conf
        storage = self._get_storage(conf)
        self.node_manager = NodeManager(storage)
        self.activity_manager = ActivityManager(storage, self.node_manager)
        self.aggregator = Aggregator(self.activity_manager,
                                     self.node_manager)

    def _get_storage(self, conf):
        storage_class = None
        for ep in iter_entry_points(group='activitystream.storage'):
            storage_class = ep.load()
            break
        storage_class = storage_class or pymongostorage.PymongoStorage
        return storage_class(conf)

    def connect(self, follower, following):
        self.node_manager.follow(follower, following)

    def disconnect(self, follower, following):
        self.node_manager.unfollow(follower, following)

    def is_connected(self, follower, following):
        return self.node_manager.is_following(follower, following)

    def create_activity(self, actor, verb, obj, target=None,
            related_nodes=None):
        return self.activity_manager.create(actor, verb, obj, target=target,
                related_nodes=related_nodes)

    def create_timeline(self, node_id):
        return self.aggregator.create_timeline(node_id)

    def get_timeline(self, *args, **kw):
        return self.aggregator.get_timeline(*args, **kw)

def configure(**conf):
    global _director
    defaults = {
            'activitystream.master': 'mongodb://127.0.0.1:27017',
            'activitystream.database': 'activitystream',
            'activitystream.activity_collection': 'activities',
            'activitystream.node_collection': 'nodes',
    }
    defaults.update(conf)
    _director = ActivityDirector(**defaults)


def director():
    global _director
    return _director

from notmm.dbapi.orm import RelationProxy, XdserverProxy

db = XdserverProxy(db_name='moviereviews')

__all__ = ['ActorManager', 'MovieCastingManager']

class ActorManager(object):
    """
    >>> actors = ActorManager.objects.all()
    """
    objects = RelationProxy(db.Actor)

    def __repr__(self):
        return "<ActorManager: %s>" % self.objects.name

class MovieCastingManager(object):
    objects = RelationProxy(db.MovieCasting)



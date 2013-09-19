from copy import copy

class NotBoundError(Exception):
    pass

class CloneableObject(object):
    """Common base class supporting automatic kwargs->attributes handling,
    and cloning."""
    attrs = ()

    def __init__(self, *args, **kwargs):
        any = lambda v: v
        for name, the_type in self.attrs:
            value = kwargs.get(name)
            if value is not None:
                setattr(self, name, (the_type or any)(value))
            else:
                try:
                    getattr(self, name)
                except AttributeError:
                    setattr(self, name, None)

    def as_dict(self, recurse=False):
        r"""Dict representation of object"""
        def f(obj, type):
            if recurse and isinstance(obj, self.__class__):
                return obj.as_dict(recurse=True)
            return type(obj) if type else obj
        return dict(
            (attr, f(getattr(self, attr), type)) for attr, type in self.attrs)


    def __copy__(self):
        return self.__class__(**self.as_dict())


    def __eq__(self, other):
        cmp(self.as_dict(), other.as_dict())

class ChannelBasedEntity(object):

    _is_bound = False
    _channel = None

    def __call__(self, channel):
        r"""Tries to bind entity to channel"""
        return self.make_bound(channel)

    def make_bound(self, channel):
        return copy(self).maybe_bind(channel)

    def revive(self, channel):
        """Revive channel after the connection has been re-established."""
        if self.is_bound:
            self._channel = channel
            self.when_bound()

    def maybe_bind(self, channel):
        if not self.is_bound and channel:
            self._channel = channel
            self.when_bound()
            self._is_bound = True
        return self

    @property
    def is_bound(self):
        return self._is_bound and self.channel is not None

    @property
    def channel(self):
        if self._channel is None:
            raise NotBoundError("Can't call method on %s not bound to a channel" % (
                self.__class__.__name__))
        return self._channel
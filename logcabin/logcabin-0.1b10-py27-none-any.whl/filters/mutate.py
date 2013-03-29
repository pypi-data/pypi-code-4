import types

from .filter import Filter

class Mutate(Filter):
    """Filter that allows you to add, rename and drop fields

    :param map set: fields to set (optional). The values if strings may format other fields from the event.
    :param map rename: fields to rename (a: b renames b to a) (optional)
    :param list unset: fields to unset (optional)
    """
    def __init__(self, set={}, rename={}, unset=[]):
        super(Mutate, self).__init__()
        self.sets = set
        assert type(self.sets) == dict
        self.renames = rename
        assert type(self.renames) == dict
        self.unsets = unset
        assert type(self.unsets) == list
    
    def process(self, event):
        for k, v in self.sets.iteritems():
            if isinstance(v, types.StringTypes):
                v = event.format(v)
            event[k] = v
            self.logger.debug('Set %r to %r' % (k, v))

        for k, v in self.renames.iteritems():
            if v in event:
                event[k] = event.pop(v)
                self.logger.debug('Renamed %r to %r' % (v, k))

        for k in self.unsets:
            if k in event:
                del event[k]
                self.logger.debug('Unset %r' % (k,))

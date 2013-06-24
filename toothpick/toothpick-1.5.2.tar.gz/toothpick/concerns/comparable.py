
class Comparable(object):
    '''
    Mixin to handle comparison operations
    '''

    def _compare(self, other, method, key_property):
        try:
            if isinstance(other, self.__class__):
                return method(getattr(self, key_property),
                              getattr(other, key_property))
            else:
                raise TypeError
        except (AttributeError, TypeError):
            # key property not implemented, or returns different type,
            # so I can't compare with "other".
            return NotImplemented

    def __lt__(self, other):
        return self._compare(other, lambda s,o: s < o, 'sort_key')

    def __gt__(self, other):
        return self._compare(other, lambda s,o: s > o, 'sort_key')

    def __le__(self, other):
        return self._compare(other, lambda s,o: s <= o, 'sort_key')

    def __ge__(self, other):
        return self._compare(other, lambda s,o: s >= o, 'sort_key')

    def __eq__(self, other):
        return self._compare(other, lambda s,o: s == o, 'equality_key')

    def __ne__(self, other):
        return self._compare(other, lambda s,o: s != o, 'equality_key')

    def __hash__(self):
        return hash((type(self), self.equality_key))

    @property
    def equality_key(self):
        return self.id

    @property
    def sort_key(self):
        return self.equality_key


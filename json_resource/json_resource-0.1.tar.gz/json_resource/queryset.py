DEFAULT_LIMIT = 10


class QuerySet(object):
    def __init__(self, resource):
        self.resource = resource

        self._exclude = []

        self._limit = DEFAULT_LIMIT
        self._offset = 0
        self._filter = {}

    def __iter__(self):
        return self

    def create(self, resource):
        raise NotImplementedError()

    def update(self, resource):
        raise NotImplementedError()

    def delete(self, resource):
        raise NotImplementedError()

    def filter(self, filter):
        self._filter.update(filter)

        return self

    def next(self):
        return self.resource(self._cursor.next())

    def exclude(self, fields):
        self._exclude += fields
        return self

    def __getitem__(self, key):
        if isinstance(key, slice):
            self._offset += key.start or 0
            if key.stop:
                self._limit = key.stop - self._offset
            return self
        else:
            if self._limit is not None and self._limit <= key:
                raise IndexError(key)

            return self.resource(self._cursor[key])

    def __get__(self, instance, owner):
        return self.__class__(self.resource)

    def __repr__(self):
        resources = []

        try:
            resources.append(self[0])
        except IndexError:
            pass

        try:
            resources.append(self[1])
        except IndexError:
            pass

        if len(self) > 2:
            resources.append('...')

        list_str = ', '.join(str(resource) for resource in resources)

        return '<%s: [%s]>' % (self.__class__.__name__, list_str)

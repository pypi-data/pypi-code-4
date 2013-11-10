class MatcherDict(object):
    def __init__(self, matcher_function):
        self._matcher = matcher_function
        self._data = []

    def get(self, key):
        for k, v in self._data:
            if self._matcher(k, key):
                return v
        else:
            raise IndexError

    def set(self, key, value):
        for i, (k, v) in enumerate(self._data):
            if self._matcher(k, key):
                self._data[i][1].append(value)
		return
        self._data.append((key, [value]))

import random

class ReservoirSample(object):
    def __init__(self, size):
        self._size = size
        self._filled = False
        self._entrynum = 0
        self._fill_i = 0
        self._l = list()
    def add(self, item):
        """ Add item to the sample. """
        if self._filled:
            i = random.randint(0, self._entrynum)
            if i < self._fill_i:
                self._l[i] = item
                res = i
            else:
                res = None
        else:
            self._l.append(item)
            res = len(self._l)
            self._fill_i = res
            if len(self._l) == self._size:
                self._filled = True
                self._fill_i = self._size
        self._entrynum += 1
        return res

    def __iter__(self):
        for i in range(self._size):
            if i >= self._fill_i:
                break
            yield self._l[i]

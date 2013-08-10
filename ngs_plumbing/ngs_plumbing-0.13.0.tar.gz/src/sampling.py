"""
This module was originally in the package
"dnasnout-client", but it is just too generally
useful to be left there.
"""
# Make Python 2 like Python 3
from __future__ import division
import sys
if sys.version_info[0] == 2:
    range = xrange

import random
import array
import bitarray
import hashlib
import operator

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

    def __len__(self):
        return self._fill_i

    def __iter__(self):
        for i in range(self._size):
            if i >= self._fill_i:
                break
            yield self._l[i]


class ReservoirSampleBloom(ReservoirSample):
    """
    Reservoir sample + Bloom filter.

    :param size: Sample size.
    :param bloom_m: Size of the bloom filter (number of bits)
    :param bloom_k: Number of hashing functions
    :param itemkey: Function taking an item and returning a string. Default is returning `item.sequence`
    :param filteronseen: If `True`, add the item to bloom filter the first time
    it is seen through the method :meth:`add`, even if not ending up
    in the sample. If `False`, only add the item to the filter if the
    item ends up in the sample.    
    
    The probabilistic insertion of an item in the sample is
    only considered if not known to the filter. A potential
    problem is that whenever the filter becomes saturated
    no new item will be inserted. The saturation of the filter
    is available through the property :attr:`saturation`.

    """
    def __init__(self, size, 
                 bloom_m = int(100E6), bloom_k = 10,
                 itemkey = operator.attrgetter('sequence'),
                 filteronseen = True):
        super(ReservoirSampleBloom, self).__init__(size)
        self._bloom_m = bloom_m
        self._bloomfilter = bitarray.bitarray(bloom_m)
        self._bloomfilter.setall(0)
        self._bloom_k = bloom_k
        self._itemkey = itemkey
        self._filteronseen = filteronseen

    def _bloom_add(self, item):
        # Note: code duplication in the _bloom_* methods
        # (to save on function calls until moved to C)
        h = hashlib.md5(self._itemkey(item))
        x = int(h.hexdigest(), 16)
        bloom_m = self._bloom_m
        bloomfilter = self._bloomfilter
        for _ in range(self._bloom_k):
            if x < bloom_m:
                h.update(b'.')
                x = int(h.hexdigest(), 16)
            x, y = divmod(x, bloom_m)
            bloomfilter[y] = 1

    def _bloom_contains(self, item):
        """ Add an item to the bloom filter 

        :param item: the item to be added.
        """
        # Note: code duplication in the _bloom_* methods
        # (to save on function calls until moved to C)
        h = hashlib.md5(self._itemkey(item))
        x = int(h.hexdigest(), 16)
        bloom_m = self._bloom_m
        res = True
        for _ in range(self._bloom_k):
            if x < bloom_m:
                h.update(b'.')
                x = int(h.hexdigest(), 16)
            x, y = divmod(x, bloom_m)
            res &= self._bloomfilter[y]
            if not res:
                break
        return res

    def _hashbits(self, item):
        # Note: code duplication in the _bloom_* methods
        # (to save on function calls until moved to C)

        h = hashlib.md5(self._itemkey(item))
        x = int(h.hexdigest(), 16)
        flag = False
        iternum = 1
        bloom_m = self._bloom_m # save lookup time
        res = list()
        for _ in range(self._bloom_k):
            if x < bloom_m:
                h.update(b'.')
                x = int(h.hexdigest(), 16)
            x, y = divmod(x, _bloom_m)
            res.append(y)
        return res

    @property
    def saturation(self):
        """ Saturation of the filter, from 0 (empty) to 1 (saturated). """
        return sum(self._bloomfilter) / len(self._bloomfilter)

    def add(self, item):
        """ Add item to the sample. 
        If the item is already in the bloom filter, it will not 
        be added.

        :param item: item to be added
        """
        if self._bloom_contains(item):
            return None
        if self._filled:
            i = random.randint(0, self._entrynum)
            if i < self._fill_i:
                self._l[i] = item
                self._bloom_add(item)
                res = i
            else:
                res = None
                if self._filteronseen:
                    self._bloom_add(item)
        else:
            self._l.append(item)
            self._bloom_add(item)
            res = len(self._l)
            self._fill_i = res
            if len(self._l) == self._size:
                self._filled = True
                self._fill_i = self._size
        self._entrynum += 1
        return res
    



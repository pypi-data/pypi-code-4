""" A priority queue implementation based off of the python binary heap, heapq.
"""

import heapq as h

class PQueue(object):
    """ Example useage:
            pq = pqueue.PQueue()
            pq.add_node(5.0, my_node)
            pq.decrease_key(2.0, my_node)
            minim = pq.get_min()
    """

    INVALID = 0
    OK = 1

    def __init__(self, data, behave="min"):
        """ Initializes a priority queue.

            Parameters
            ----------
            data : list
                List of the form (weight, PQueue.OK, node)

            behave : str (optional, default="min")
                Specifiy the behavior of the priority queue. Should either be
                'min' or 'max'.

            Returns
            -------
            pqueue : PQueue
                Instance of a priority queue.
        """
        self._bhv = behave
        self._current = 0

        if self._bhv == "min":
            self._pq = [[wght, PQueue.OK, nd] for wght, nd in data]
        elif self._bhv == "max":
            self._pq = [[-wght, PQueue.OK, nd] for wght, nd in data]

        h.heapify(self._pq)
        self._node_finder = dict([(nd, [wght, st, nd]) \
                for wght, st, nd in self._pq])

    def __str__(self):
        return str(self._pq)

    def __repr__(self):
        return str(self._pq)

    def __len__(self):
        return len(self._node_finder)

    def __iter__(self):
        return self

    def add_node(self, weight, node, state=OK):
        """ adds a node with the given weight to the
            priority queue. the default state of OK is
            used, unless a node need be marked invalid
        """
        # we use a triple to maintain the state of the node
        # this will allow use to decrease the weight of a
        # node in O(log n) time still
        if self._bhv == "min":
            entry = [weight, state, node]
        else:
            entry = [-weight, state, node]
        self._node_finder[node] = entry
        h.heappush(self._pq, entry)

    def get_min(self):
        """ return the minimum weighted node in the
            priority queue and remove it from the
            heap
        """
        while self._pq:
            weight, state, node = h.heappop(self._pq)
            # only retrieve nodes with an OK state
            if state == PQueue.OK and node in self._node_finder:
                del self._node_finder[node]
                if self._bhv == "min":
                    return node, weight
                else:
                    return node, -weight

        return None, None

    def get_max(self):
        return self.get_min()

    def min(self):
        """ return the minimum weighted node in the
            priority queue without removing it from the
            heap
        """
        for weight, count, node in self._pq:
            if count != PQueue.INVALID:
                if self._bhv == "min":
                    return node, weight
                else:
                    return node, -weight
            else:
                del self._node_finder[node]

    def max(self):
        return self.min()

    def delete_node(self, node):
        """ delete a node from the priority queue
        """
        # really it just gets marked invalid
        entry = self._node_finder[node]
        entry[1] = PQueue.INVALID

    def decrease_key(self, weight, node):
        """ decrease the weight of a given
            node in the priority queue
        """
        entry = self._node_finder[node]
        self.add_node(weight, node, entry[1])
        entry[1] = PQueue.INVALID

    def next(self):
        """
        """
        if self._current == len(self):
            self._current = 0
            raise StopIteration
        else:
            # we want to skip the invalid data
            st = PQueue.INVALID
            while st == PQueue.INVALID:
                val, st, key = self._pq[self._current]
                self._current += 1

                if self._current == len(self):
                    self._current = 0
                    raise StopIteration

            return key, val

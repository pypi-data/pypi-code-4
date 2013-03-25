from __future__ import print_function

import banyan_c


class MinGapUpdator(object):
    """
    Updates nodes by the minimum, maximum, and min-gaps of their subtrees. Allows trees employing this to           
        efficiently answer what is the smallest gap in their keys.
        
    Example:
    
    >>> t = SortedSet([1, 3, 2], updator = MinGapUpdator)
    >>> 
    >>> t
    SortedSet([1, 2, 3])
    >>> print(t.min_gap())
    1
    >>> 
    >>> t.remove(2)
    >>> t
    SortedSet([1, 3])
    >>> print(t.min_gap())
    2
    >>> t.add(20)
    >>> t
    SortedSet([1, 3, 20])
    >>> print(t.min_gap())
    17
    
    .. Note::
        
        The keys used with this updator must support the `number protocol`_ and be `rich comparable`_, otherwise an exception will be thrown.
        
        .. _`number protocol`: http://docs.python.org/2/c-api/number.html
        .. _`rich comparable`: http://docs.python.org/2/c-api/object.html?highlight=pyobject_richcomparebool#PyObject_RichCompareBool
        
        Example:
        
        >>> t = SortedSet(['1', '3', '2'], updator = MinGapUpdator)
    """        

    # Metadata appended to each node.
    class Metadata(banyan_c.MinGapMetadata):
        # Overwritten by C implementation
        pass
        
    def min_gap(self):
        """
        :returns: Smallest gap between the keys.
        :raises: :py:exc:`RuntimeError` if there are fewer than two keys in the set.
        
        Example:
        
        >>> t = SortedSet([1, 3, 2], updator = MinGapUpdator)
        >>>
        >>> t.min_gap()
        >>> 1
        >>> t.erase(2)
        >>> t.min_gap()
        2
        >>> t.erase(1)
        >>> t.min_gap()
        ddff
        """
        return self._min_gap_updator_min_gap()
                


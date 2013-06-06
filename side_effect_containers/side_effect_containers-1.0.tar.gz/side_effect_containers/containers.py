""" Copyright (c) 2013 Josh Matthias <jmatthias4570@gmail.com> """

_NotSet = object()

def slice_from_slice_or_index(i):
    """ Accept either an index or a slice. Always return a slice. """
    if isinstance(i, slice):
        return i
    
    end_index = i + 1 or None
    
    return slice(i, end_index)

class SideEffectSet(set):
    """ A set that performs an action every time an element is added or removed.
        
        If you wish to bypass this class's methods and make a change to the
        set without any side effects, use the appropriate method of the 'set'
        builtin type. Example:
            Instead of this:    side_effect_set_instance.add(item)
            ... do this:        set.add(side_effect_list_instance, item)
        
        Subclasses must implement the following methods:
            _add_element(self, elem)
            _remove_element(self, elem)
        """
    
    def _add_all(self, iterable):
        for item in iterable: self._add_element(item)
    
    def _remove_all(self, iterable):
        for item in iterable: self._remove_element(item)
    
    def add(self, elem):
        set.add(self, elem)
        self._add_element(elem)
    
    def remove(self, elem):
        set.remove(self, elem)
        self._remove_element(elem)
    
    def discard(self, elem):
        if elem in self:
            self.remove(elem)
    
    def pop(self):
        elem = set.pop(self)
        self._remove_element(elem)
        return elem
    
    def clear(self):
        old_set = set(self)
        set.clear(self)
        self._remove_all(old_set)
    
    def __ior__(self, other):
        new_set = other - self
        
        self._add_all(new_set)
        
        return set.__ior__(self, other)
    
    def __iand__(self, other):
        old_set = self - other
        
        self._remove_all(old_set)
        
        return set.__iand__(self, other)
    
    def __isub__(self, other):
        old_set = self & other
        
        self._remove_all(old_set)
        
        return set.__isub__(self, other)
    
    def __ixor__(self, other):
        old_set = self & other
        new_set = other - self
        
        self._remove_all(old_set)
        self._add_all(new_set)
        
        return set.__ixor__(self, other)
    
    def update(self, other):
        self |= set(other)
    
    def intersection_update(self, other):
        self &= set(other)
    
    def difference_update(self, other):
        self -= set(other)
    
    def symmetric_difference_update(self, other):
        self ^= set(other)
    
    def replace(self, other):
        """ Replace all elements of 'self' with all elements of 'other'. """
        self.update(other)
        self.intersection_update(other)

class SideEffectList(list):
    """ A list that performs a side action every time a value is added, removed,
        or changed.
        
        If you wish to bypass this class's methods and make a change to the
        list without any side effects, use the appropriate method of the 'list'
        builtin type. Example:
            Instead of this:    side_effect_list_instance.append(item)
            ... do this:        list.append(side_effect_list_instance, item)
        
        Subclasses must implement this method:
            _replace_sequence(self, old_sequence, new_sequence, seq_slice)
        """
    def append(self, item):
        self[len(self):len(self)] = [item]
    
    def extend(self, iterable):
        self[len(self):len(self)] = iterable
    
    def insert(self, i, item):
        self[i:i] = [item]
    
    def pop(self, i=-1):
        result = self[i]
        del self[i]
        return result
    
    def remove(self, item):
        del self[self.index(item)]
    
    def clear(self):
        del self[:]
    
    def __setslice__(self, i, j, sequence):
        self.__setitem__(slice(i, j), sequence)
    
    def __delslice__(self, i, j):
        self.__delitem__(slice(i, j))
    
    def __setitem__(self, i, item):
        seq_slice = slice_from_slice_or_index(i)
        
        old_sequence = self[seq_slice]
        if isinstance(i, slice):
            new_sequence = item
        else:
            new_sequence = [item]
        
        new_sequence = self._before_replace_routine(new_sequence)
        
        super().__setitem__(seq_slice, new_sequence)
        
        self._replace_sequence(old_sequence, new_sequence, seq_slice)
    
    def __delitem__(self, i):
        seq_slice = slice_from_slice_or_index(i)
        self[seq_slice] = []
    
    def _before_replace_routine(self, new_sequence):
        return new_sequence

class SideEffectDict(dict):
    """ A dict that performs a side action every time a value is added, removed,
        or changed.
        
        If you wish to bypass this class's methods and make a change to the
        dict without any side effects, use the appropriate method of the 'dict'
        builtin type. Example:
            Instead of this:
                side_effect_dict_instance['key'] = value
            
            ... do this:
                dict.__setitem__(side_effect_dict_instance, 'key', value)
        
        Subclasses must implement this method:
            _replace_value(self, new_value, key)
        
        The '_before_replace' method allows you to examine a key, value pair
        before actually performing the replacement.
        """
    
    def _before_replace(self, new_value, key):
        return new_value
    
    def __setitem__(self, key, value):
        old_value = self.get(key)
        new_value = self._before_replace(value, key)
        
        super().__setitem__(key, new_value)
        
        self._replace_value(old_value, new_value, key)
    
    def __delitem__(self, key):
        old_value = self.get(key)
        
        super().__delitem__(key)
        
        self._remove_value(old_value, key)
    
    def setdefault(self, key, default=None):
        try:
            result = self[key]
        except KeyError:
            result = default
            self[key] = default
        
        return result
    
    def update(self, other={}):
        new_dict = dict(other)
        for key, value in new_dict.items():
            self[key] = value
    
    def pop(self, key, default=_NotSet):
        try:
            result = self[key]
        except KeyError:
            if default is _NotSet:
                raise
            
            result = default
        else:
            del self[key]
        
        return result
    
    def popitem(self):
        item = dict(self).popitem()
        del self[item[0]]
        return item
    
    def clear(self):
        for key in list(self.keys()):
            del self[key]








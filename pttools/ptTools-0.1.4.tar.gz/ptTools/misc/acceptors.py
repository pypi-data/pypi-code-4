#!/usr/bin/env python3

"""Module providing regular-language-acceptor classes.

The acceptors provided by this module can be used to construct
acceptors for matching words of regular languages.  The following,
common regular operations are supported:

    - Concatenation
    - Union
    - Positive closure
    - Kleene closure
    - Repetition
    - Option

None of these operations is mutable.  They all return full, structural
copies of the acceptors and their successors.

To construct an acceptor, instantiate ``Single`` with any object that
has an ``__eq__`` method.  The acceptor returned by ``Single(obj)``
matches an object wrapped in an indexable collection if
``obj.__eq__(other)`` yields True.

>>> t = Single(True)
>>> t.accepts([True,])
True
>>> ## t.accepts(True) ## TypeError: 'bool' object is not subscriptable

That we must match against indexables becomes apparent, when we
concatenate acceptors.  Technically, the collection to match against
is passed through the acceptor compound.  Each acceptor - be it a
single acceptor, a closure, or other - matches the longest slice
possible, starting with the first unmatched item.

>>> f = Single(False)
>>> tf = t + f
>>> tf.accepts([True, False])
True

The regular operations map to infix and prefix operators as follows:

    - Concatenation    :: __add__    :: r + s
    - Union            :: __or__     :: r | s
    - Positive closure :: __pos__    :: +r
    - Kleene closure   :: __invert__ :: ~r
    - Repetition       :: __mul__    :: r * n
    - Option           :: __neg__    :: -r

Note that a union of acceptors backtracks from failed matched to
continue with remaining options.

"""

__author__ = "Markus Rother - python@markusrother.de"
__date__ = "06/2013"
__version__ = "0.1"

__all__ = [
    'RegularLanguageAcceptor',
    'AbstractSingle',    
    'Compound',    
    'Final',    
    'Single',
    'Test',
    'Union',
    ]

import collections

class RegularLanguageAcceptor(object):

    """Class for non-deterministic acceptors of regular languages."""

    def __add__(self, other):
        """Prefix '+' operator for concatenating two acceptors.

        >>> rs = Single('r') + Single('s')
        >>> rs.accepts('rs')
        True
        
        """
        return self._concat(other)

    def __invert__(self):
        """Prefix '~' operator for creating a kleene closure over an
        acceptor.

        >>> rx = ~Single('r')
        >>> all((rx.accepts(x) for x in ['','r','rrr']))
        True

        """        
        return self._kleene_closure()

    def __mul__(self, k):
        """Binary '*' operator for repeating an acceptor n times.

        >>> rx = Single('r') * 3
        >>> rx.accepts('rrr')
        True
        >>> rx.accepts('r')
        False

        """        
        return self._repeat(k)

    def __neg__(self):
        """Prefix '-' operator for making acceptor optional.

        >>> rx = -Single('r')
        >>> rx.accepts('')
        True
        >>> rx.accepts('r')
        True
        >>> rx.accepts('rr')
        False

        """        
        return self._option()
    
    def __or__(self, other):
        """Binary '|' operator for creating a union of two acceptors.

        >>> rx = Single('r') | Single('s')
        >>> rx.accepts('r')
        True
        >>> rx.accepts('s')
        True

        """        
        return self._union(other)

    def __pos__(self):
        """Prefix '+' operator for creating a positive closure over an
        acceptor.

        >>> rx = +Single('r')
        >>> all((rx.accepts(x) for x in ['r','rrr']))
        True
        >>> rx.accepts('')
        False

        """        
        return self._positive_closure()

    def _accepts(self, *ignore):
        """Raises AttributeError."""
        self._subclass_responsibility()

    def _concat(self, other):
        """Returns regular language concatenation of self with other."""
        head = self.copy()
        tail = other.copy()
        head.replace_all_final(tail)
        return head

    def _copy(self, dict):
        """Creates copy of self, and adds it into dict, unless already
        present.  Returns copy."""
        copy = dict.get(self)
        if not copy:
            cls = self.__class__
            copy = cls.__new__(cls)
            dict[self] = copy
            self._copy_attributes_into(copy, dict)
        return copy

    def _copy_attributes_into(self, copy, dict, *args, **kwargs):
        """Raises AttributeError."""
        copy.__init__(*args, **kwargs)

    def _do_if(self, fn, cond, recur):
        """Applies fn to all acceptors in self."""
        if self in recur: 
            return False
        elif not cond(self):
            recur.add(self)
            return False
        else:
            recur.add(self)
            fn(self)
            return True

    def _kleene_closure(self):
        """Returns kleene closure over self."""
        return self.union_class(self._positive_closure(), self.final_class())

    def _option(self):
        """Returns regular language option of self."""
        return self.union_class(self.copy(), self.final_class())        

    def _path_of(self, *ignore):
        """Raises AttributeError."""
        self._subclass_responsibility()

    def _positive_closure(self):
        """Returns positive closure over self."""        
        closure = self.copy()
        union = self.union_class(closure, self.final_class())
        closure.do_if(lambda s : s._replace_all_final(union),
                      lambda s : s is not union)
        return closure

    def _replace_all_final(self, *ignore):
        """Raises AttributeError."""
        self._subclass_responsibility()

    def _repeat(self, k):
        """Returns concatenation of k repetitions of self."""
        repetition = self
        for i in range(k-1):
            repetition += self
        return repetition

    def _subclass_responsibility(self):
        """Raises AttributeError. (Development only)."""
        import inspect
        caller = inspect.stack()[1][3]
        msg ='\'{}\' object has no attribute \'{}\''
        raise AttributeError(msg.format(self.__class__.__name__, caller))

    def _union(self, other):
        """Returns regular language union of self and other."""        
        if isinstance(other, Union):
            ## Redirecting for convenience to avoid nested Unions.
            return other.__or__(self)
        else:
            return Union(self, other)

    @property    
    def final_class(self):
        """Returns class to instantiate final acceptor from."""
        return Final

    @property
    def final_states(self):
        """Returns list of all final acceptors in self."""
        return self.states_of_type(self.final_class)

    @property
    def single_class(self):
        """Returns class to instantiate acceptor from."""
        return Single
    
    @property
    def states(self):
        """Returns list of all acceptors in self."""
        return self.states_if(lambda s : True)

    @property
    def union_class(self):
        """Returns class to instantiate union from."""        
        return Union
        
    def accepts(self, word):
        """True, if self accepts word."""
        return self._accepts(word)

    def copy(self):
        """Returns full copy of self."""
        dict = {}
        self._copy(dict)
        return dict[self]
        
    def do(self, fn):
        """Traverses acceptors in self, applying fn to each acceptor."""
        self.do_if(fn, lambda s : True)

    def do_if(self, fn, cond):
        """Iterates over all acceptors in self, applying fn(acc) if
        cond(acc) is met."""
        self._do_if(fn, cond, set())

    def isfinal(self):
        """Returns False."""
        return False

    def path_of(self, word):
        """True, if matches word.  Returns list of tuples of
        acceptors, and the input each of them matched.

        The returned list is the accepting path taken through self.
        The input matched may be either a slice or an item of the word
        matched.
        
        """
        path = []
        self._path_of(word, path)
        return path

    def replace_all_final(self, new):
        """Replaces all final acceptors in self with new."""
        self.do_if(lambda s : s._replace_all_final(new),
                   lambda s : s is not new)

    def states_if(self, fn):
        """Returns list of all acceptors in self if condition applies."""
        l = []
        recur = set()
        self.do(lambda s : l.append(s) if fn(s) else None)
        return l

    def states_of_type(self, type):
        """Returns list of all acceptors of given type in self."""
        return self.states_if(lambda s : isinstance(s, type))

    def validate_word(self, word):
        """Raises AttributeError if given word is invalid."""
        if isinstance(word, str) or \
           isinstance(word, list) or \
           isinstance(word, tuple) or \
           word is None:
            return
        else:
            raise AttributeError('Invalid word')
        

class Final(RegularLanguageAcceptor):

    """Acceptor that accepts the empty word and has no successors."""

    def __mod__(self, ignore):
        return self

    def _accepts(self, word):
        """True, if word is consumed."""
        return not bool(word)

    def _path_of(self, word, path):
        """True, if matches word.  Appends tuple of self, and matched
        input to path."""
        if self._accepts(word):
            path.append((self, None))
            return True
        else:
            return False                    

    def _replace_all_final(self, ignore):
        """Ignore.  Ends recursion."""
        return

    def isfinal(self):
        """Returns True."""
        return True


class AbstractSingle(RegularLanguageAcceptor):

    """Acceptors with one successor."""

    def __init__(self, successor=None, **kwargs):
        self.successor = successor if successor else self.final_class()
        super().__init__(**kwargs)

    def _copy_attributes_into(self, copy, dict, *args, **kwargs):
        """Writes self's attributes into copy."""
        kwargs['successor'] = self.successor._copy(dict)
        super()._copy_attributes_into(copy, dict, *args, **kwargs)

    def _do_if(self, fn, cond, recur):
        """Applies fn to all acceptors in self."""
        if super()._do_if(fn, cond, recur):
            self.successor._do_if(fn, cond, recur)
            return True
        else:
            return False

    def _replace_all_final(self, new):
        """Replaces successor with new if it is final."""
        if self is new:
            return
        elif self.successor.isfinal():
            self.successor = new


class Test(AbstractSingle):

    """Acceptors with a test function.  Matches item from word if
    fn(item) yields True."""

    def __init__(self, fn, **kwargs):
        if isinstance(fn, collections.Callable):
            self.fn = fn
            super().__init__(**kwargs)
        else:
            raise TypeError('Test expects function, got {}'.format(fn))
        
    def _accepts(self, word):
        """True, if self matches first item, and successors match
        rest."""
        if not word or not self._test(word[0]):
            return False
        else:
            return self.successor._accepts(word[1:])

    def _copy_attributes_into(self, copy, dict, *args, **kwargs):
        """Returns new instance of self.__class__, initialized with
        self.fn."""
        kwargs['fn'] = self.fn
        super()._copy_attributes_into(copy, dict, *args, **kwargs)

    def _path_of(self, word, path):
        """True, if matches word.  Appends tuple of self, and matched
        input to path."""
        if not word or not self._test(word[0]):
            return False
        else:
            temp = []
            if self.successor._path_of(word[1:], temp):
                path.append((self, word[0]))
                path.extend(temp)
                return True
            else:
                return False
    
    def _test(self, obj):
        """Returns self.fn(obj).

        Beware!        

        >>> ().__eq__([])
        NotImplemented
        >>> [].__eq__(())
        NotImplemented
        >>> bool(NotImplemented)
        True

        >>> () == []
        False
        >>> bool(().__eq__([])) ## WTF!
        True
        
        """
        return self.fn(obj)


class Single(Test):

    """Acceptor to match an item from a given word.
    
    Instantiate Single with any object that has an __eq__ method.  The
    acceptor returned by Single(obj) matches an item if
    obj.__eq__(other) yields True.

    """

    def __init__(self, value, fn=None, **kwargs):
        self.value = value
        kwargs.setdefault('fn', value.__eq__ if not fn else fn)
        super().__init__(**kwargs)

    def _copy_attributes_into(self, copy, dict, *args, **kwargs):
        """Writes self's attributes into copy."""
        kwargs['value'] = self.value
        super()._copy_attributes_into(copy, dict, *args, **kwargs)
        

class Union(RegularLanguageAcceptor):

    """Acceptor to match the regular union of two or more acceptors."""

    def __init__(self, *options, **kwargs):
        super().__init__(**kwargs)
        self.options = []
        self.options.extend(options)

    def __or__(self, other):
        """Binary '|' operator for creating a union of two acceptors."""
        ## Reimplemented to avoid nested unions.
        self.options.append(other)
        return self

    def _accepts(self, word):
        """True, if one of selfs options matches word."""
        return any((option._accepts(word) for option in self.options))

    def _copy_attributes_into(self, copy, dict, **kwargs):
        """Writes self's attributes into copy."""
        args = [option._copy(dict) for option in self.options]
        super()._copy_attributes_into(copy, dict, *args, **kwargs)

    def _do_if(self, fn, cond, recur):
        """Applies fn to all acceptors in self."""
        if super()._do_if(fn, cond, recur):
            for succ in self.options:
                succ._do_if(fn, cond, recur)

    def _path_of(self, word, path):
        """True, if matches word.  Appends tuple of self, and matched
        input to path, if matches."""
        if not word:
            for option in self.options:
                if option.isfinal():
                    option._path_of(word, path)
                    return True
        for option in self.options:
            temp = []
            if option._path_of(word, temp):
                path.append((self, word))
                path.extend(temp)
                return True
        return False

    def _replace_all_final(self, new):
        """Replaces all final acceptors in self.options with new."""        
        for idx,succ in enumerate(self.options):
            if succ.isfinal():
                self.options[idx] = new


class Compound(AbstractSingle):

    """Wrapper for acceptors.  Implemented for easier subclassing."""
    
    def __init__(self, inner, **kwargs):
        ## TODO - When instantiating, inners final states should be
        ## replaced by a compound exist.  Currently, we cannot
        ## determine when the compound is left.  What we are looking
        ## for, is somewhat like strong components of the acceptor.
        super().__init__(**kwargs)
        self.inner = inner

    def _accepts(self, word):
        """True, if self.inner matches word."""
        return self.inner._accepts(word)

    def _copy_attributes_into(self, copy, dict, **kwargs): 
        """Writes self's attributes into copy."""
        kwargs['inner'] = self.inner._copy(dict)
        super()._copy_attributes_into(copy, dict, **kwargs)

    def _path_of(self, word, path):
        """True, if matches word.  Appends tuple of self, and matched
        input to path, if matches."""        
        temp = []
        if self.inner._path_of(word, temp):
            path.append((self, word))
            path.extend(temp)
            return True
        else:
            return False

    @property
    def inner(self):
        return self.successor

    @inner.setter
    def inner(self, acceptor):
        self.successor = acceptor


# -*- coding: utf-8 -*-
"""Generic functions and multi methods.

This module was snarfed from:
<http://svn.python.org/view/*checkout*/sandbox/trunk/overload/overloading.py?content-type=text%2Fplain&rev=43727>

The original doc string follows:

Dynamically overloaded functions.

This is an implementation of (dynamically, or run-time) overloaded
functions; also known as generic functions or multi-methods.

The dispatch algorithm uses the types of all argument for dispatch,
similar to (compile-time) overloaded functions or methods in C++ and
Java.

Most of the complexity in the algorithm comes from the need to support
subclasses in call signatures.  For example, if an function is
registered for a signature (T1, T2), then a call with a signature (S1,
S2) is acceptable, assuming that S1 is a subclass of T1, S2 a subclass
of T2, and there are no other more specific matches (see below).

If there are multiple matches and one of those doesn't *dominate* all
others, the match is deemed ambiguous and an exception is raised.  A
subtlety here: if, after removing the dominated matches, there are
still multiple matches left, but they all map to the same function,
then the match is not deemed ambiguous and that function is used.
Read the method find_func() below for details.

Python 2.5 is required due to the use of predicates any() and all().
"""


from itertools import izip as zip
from types import FunctionType
from inspect import getargspec


class GenericFunction(object):
    """An implementation of generic functions.
    """

    def __init__(self, default_func=None, name=None):
        # Decorator to declare new overloaded function.
        self.registry = {}
        self.variadics = {}
        self.arities = set()
        self.cache = {}
        self.name = name
        self.default_func = default_func

    def method(self, *types):
        """Decorator to register a method for a specific set of types.
        """
        
        def helper(function):
            self.register_func(types, function, False)
            return self.substitute
            
        return helper

    def variadic_method(self, *types):
        """Decorator to register a method for a specific set of types.
        
        The method has a variable argument count.
        """
        
        def helper(function):
            self.register_func(types, function, True)
            return self.substitute
            
        return helper

    def register_func(self, types, func, variadic):
        """Helper to register an implementation."""
        if self.name is None:
            self.name = "%s.%s" % (func.__module__, func.__name__)
            self.substitute.__name__ = func.__name__
        if self.substitute.__doc__ and func.__doc__:
            doc = "\n\n"
            if not self.registry:
                doc += "Multi methods:\n\n"
            doc += ".. function:: %s.%s(%s)" % (func.__module__, func.__name__,
                    ", ".join(("%s: %s" % (arg, type.__name__)
                        for arg, type in zip(getargspec(func)[0], types))))
            doc += "\n\n"
            doc += "\n".join(
                    " " * 4 + line for line in func.__doc__.split("\n"))
            self.substitute.__doc__ += doc
        self.registry[tuple(types)] = func
        if variadic:
            self.variadics[tuple(types)] = func
            self.arities.discard(len(types))
        self.cache = {} # Clear the cache (later we can optimize this).

    def __call__(self, *args):
        """Call the overloaded function."""
        types = tuple(map(type, args))
        func = self.cache.get(types)
        if func is None:
            self.cache[types] = func = self.find_func(types)
        return func(*args)

    def super(self, *types):
        """Answer a specific (base) method that for the types passed."""
        return self.find_func( types )

    def _fix_variadics(self, arity):
        """Fix the registry for all the variadic functions.
        
        Don't touch the cache, we never processed functions
        with this `arity`."""
        if arity not in self.arities:
            for sig, function in self.variadics.iteritems():
                sig_len = len(sig)
                if sig_len < arity:
                    new_sig = sig + (object,) * (arity - len(sig))
                    if new_sig not in self.registry:
                        self.registry[new_sig] = function
            self.arities.add(arity)

    def find_func(self, types):
        """Find the appropriate overloaded function; don't call it.
        
        This won't work for old-style classes or classes without __mro__.
    
        """
        func = self.registry.get(types)
        if func is not None:
            # Easy case -- direct hit in registry.
            return func
    
        # XXX Phillip Eby suggests to use issubclass() instead of __mro__.
        # There are advantages and disadvantages.
    
        self._fix_variadics(len(types))
        # I can't help myself -- this is going to be intense functional code.
        # Find all possible candidate signatures.
        mros = tuple(t.__mro__ for t in types)
        n = len(mros)
        candidates = [sig for sig in self.registry
                      if len(sig) == n and
                         all(t in mro for t, mro in zip(sig, mros))]
        if not candidates:
            # No match at all -- use the default function.
            answer = self.default_func
            if answer is None:

                def answer(*arguments):
                    raise NotImplementedError( 
                            "Generic %r has no implementation for type(s): %s" % (
                                self.name,
                                ", ".join(  "%s.%s" % (
                                    parameterType.__module__,
                                    parameterType.__name__ )
                                for parameterType in types )))

            return answer
        if len(candidates) == 1:
            # Unique match -- that's an easy case.
            return self.registry[candidates[0]]
    
        # More than one match -- weed out the subordinate ones.
    
        def dominates(dom, sub,
                      orders=tuple(dict((t, i) for i, t in enumerate(mro))
                                   for mro in mros)):
            # Predicate to decide whether dom strictly dominates sub.
            # Strict domination is defined as domination without equality.
            # The arguments dom and sub are type tuples of equal length.
            # The orders argument is a precomputed auxiliary data structure
            # giving dicts of ordering information corresponding to the
            # positions in the type tuples.
            # A type d dominates a type s iff order[d] <= order[s].
            # A type tuple (d1, d2, ...) dominates a type tuple of equal length
            # (s1, s2, ...) iff d1 dominates s1, d2 dominates s2, etc.
            if dom is sub:
                return False
            return all(order[d] <= order[s]
                       for d, s, order in zip(dom, sub, orders))
    
        # I suppose I could inline dominates() but it wouldn't get any clearer.
        candidates = [cand
                      for cand in candidates
                      if not any(dominates(dom, cand) for dom in candidates)]
        if len(candidates) == 1:
            # There's exactly one candidate left.
            return self.registry[candidates[0]]
    
        # Perhaps these multiple candidates all have the same implementation?
        funcs = set(self.registry[cand] for cand in candidates)
        if len(funcs) == 1:
            return funcs.pop()
    
        # No, the situation is irreducibly ambiguous.
        raise TypeError("ambiguous call to generic %r; types=%r; candidates=%r" %
                        (self.name, types, candidates))

    def callmapped(self, mapper, *arguments):
        """Call the overloaded function, with a mapper passed explicitly."""
        types = tuple(map(type, arguments))
        function = self.cache.get(types)
        if function is None:
            self.cache[types] = function = self.find_func(types)
        return function(*(mapper(argument)
                for argument in arguments))
    

def _generic(defaultFunction=None, name=None, doc=None):
    """Answer a generic function, that is a real function object.
    """
    
    genericFunction = GenericFunction(defaultFunction, name)
    
    def substitute(*arguments):
        return genericFunction(*arguments)
    
    substitute.method = genericFunction.method
    substitute.variadic_method = genericFunction.variadic_method
    substitute.super = genericFunction.super
    if defaultFunction is not None:
        substitute.__name__ = defaultFunction.__name__
        substitute.__doc__ = defaultFunction.__doc__
    else:
        if name is not None:
            substitute.__name__ = name
        if doc is not None:
            substitute.__doc__ = doc
    genericFunction.substitute = substitute
    return substitute

def method(*types):
    """Automatically call the `method´ method of a generic function.

    This function is intended to be used as a decorator.
    """
    
    def helper(function):
        return find_generic(function).method(*types )(function)
            
    return helper

def variadic_method(*types):
    """Automatically call the `variadic_method´ method of a generic function.

    This function is intended to be used as a decorator.
    """
    
    def helper(function):
        return find_generic(function).variadic_method(*types )(function)
            
    return helper

@_generic
def find_generic(someObject):
    """Find the generic function for some function with the same name,
    """
    raise NotImplementedError(
            "Can't find the generic function for %s" % type(someObject))


@find_generic.method(FunctionType)
def find_generic(function):
    #d#import pdb; pdb.set_trace()
    try:
        name = function.__name__
        return function.func_globals[name]
    except KeyError:
        raise TypeError(
                "Can't find a generic function for method named %s" %
                    function.__name__)


generic = _generic(name="generic")

@method(FunctionType)
def generic(default_function):
    return _generic(default_function)

@method(type)
def generic(newstyle_class):
    return _generic(newstyle_class)

@method()
def generic():
    return _generic()

@method(basestring)
def generic(function_name):
    return _generic(name=function_name)

@method(basestring, basestring)
def generic(function_name, doc):
    return _generic(name=function_name, doc=doc)

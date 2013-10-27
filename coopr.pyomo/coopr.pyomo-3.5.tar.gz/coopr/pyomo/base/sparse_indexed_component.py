#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['SparseIndexedComponent', 'ActiveSparseIndexedComponent']

import pyutilib.misc
from six import iterkeys, itervalues

from coopr.pyomo.base.component import Component
from coopr.pyomo.base.sets import Set
from coopr.pyomo.base.indexed_component import IndexedComponent, UnindexedComponent_set

def process_setarg(arg):
    """
    Process argument and return an associated set object.
    """
    if isinstance(arg,Set):
        # Argument is a Set instance
        return arg
    elif isinstance(arg,IndexedComponent) or \
            isinstance(arg,SparseIndexedComponent):
        raise TypeError("Cannot index a component with a non-set component")
    else:
        try:
            # Argument has set_options attribute, which is used to initialize the set
            options = getattr(arg,'set_options')
            options['initialize'] = arg
            return Set(**options)
        except:
            pass
    # Argument is assumed to be an initialization function
    return Set(initialize=arg)


class SparseIndexedComponent(Component):
    """
    This is the base class for all indexed modeling components.

    Constructor arguments:
        ctype       The class type for the derived subclass
        doc         A text string describing this component

    Private class attributes:
        _data       A dictionary from the index set to component data objects
        _index      The set of valid indices
    """

    #
    # defaults are nice from a user perspective, but they are not nice from
    # a performance perspective. in particular, if an index is supplied
    # for which there is not a _data entry (specifically, in a get call),
    # then you have to resort to checking the input index for containment
    # in the index set. this is extremely expensive, and is something
    # that performance-conscious users may want to explicitly avoid. 
    # use with care!
    #
    _DEFAULT_INDEX_CHECKING_ENABLED = True

    def __init__(self, *args, **kwds):
        Component.__init__(self, **kwds)
        #
        self._data = {}
        #
        if len(args) == 0:
            #
            # If no indexing sets are provided, generate a dummy index
            #
            self._implicit_subsets = None
            self._index = UnindexedComponent_set
            self._data = {None: None}
        elif len(args) == 1:
            self._implicit_subsets = None
            self._index = process_setarg(args[0])
        else:
            # NB: Pyomo requires that all modelling components are
            # assigned to the model.  The trick is that we allow things
            # like "Param([1,2,3], range(100), initialize=0)".  This
            # needs to create *3* sets: two SetOf components and then
            # the SetProduct.  That means that the component needs to
            # hold on to the implicit SetOf objects until the component
            # is assigned to a model (where the implicit subsets can be
            # "transferred" to the model).
            tmp = [process_setarg(x) for x in args]
            self._implicit_subsets = tmp
            self._index = tmp[0].cross(*tmp[1:])

    def clear(self):
        """Clear the data in this component"""
        if UnindexedComponent_set != self._index:
            self._data = {}
        else:
            raise NotImplementedError(
                "Derived singleton component %s failed to define clear().\n"
                "\tPlease report this to the Pyomo developers"
                % (self.__class__.__name__,))

    def __len__(self):
        return len(self._data)

    def __contains__(self, ndx):
        return ndx in self._data

    def __iter__(self):
        return self._data.__iter__()

    #
    # NB: The standard access / iteration methods iterate over the
    # the keys of self._data, which may be a subset of self._index.
    #
    
    def keys(self):
        return [ x for x in self ]

    def values(self):
        return [ self[x] for x in self ]

    def items(self):
        return [ (x, self[x]) for x in self ]

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        for key in self:
            yield self[key]
    
    def iteritems(self):
        for key in self:
            yield key, self[key]

    def __getitem__(self, ndx):
        """
        This method returns the data corresponding to the given index.
        """
        if ndx in self._data:
            if ndx is None:
                return self
            else:
                return self._data[ndx]
        elif not self._constructed:
            # FIXME: Ideally, we would like to check the _constructed
            # flag first, but that breaks many things; in particular,
            # PyomoModel.clone() for unconstructed models (30 Sept 2013)
            if ndx is None:
                idx_str = ''
            elif ndx.__class__ is tuple:
                idx_str = "[" + ",".join(str(i) for i in ndx) + "]"
            else:
                idx_str = "[" + str(ndx) + "]"
            raise ValueError(
                "Error retrieving component %s%s: The component has "
                "not been constructed." % ( self.cname(True), idx_str,) )
        elif not SparseIndexedComponent._DEFAULT_INDEX_CHECKING_ENABLED:
            return self._default(ndx)            
        elif ndx in self._index:
            return self._default(ndx)
        else:
            ndx = self.normalize_index(ndx)
            if ndx in self._data:
                if ndx is None:
                    return self
                else:
                    return self._data[ndx]
            if ndx in self._index:
                return self._default(ndx)

        if not self.is_indexed():
            msg = "Error accessing indexed component: " \
                  "Cannot treat the scalar component '%s' as an array" \
                  % ( self.cname(True), )
        else:
            msg = "Error accessing indexed component: " \
                  "Index '%s' is not valid for array component '%s'" \
                  % ( ndx, self.cname(True), )
        raise KeyError(msg)

    def _default(self, index):
        raise NotImplementedError(
            "Derived component %s failed to define _default().\n"
            "\tPlease report this to the Pyomo developers"
            % (self.__class__.__name__,))

    def normalize_index(self, index):
        ndx = pyutilib.misc.flatten(index)
        if type(ndx) is list:
            if len(ndx) == 1:
                ndx = ndx[0]
            else:
                ndx = tuple(ndx)
        return ndx

    def index_set(self):
        """Return the index set"""
        return self._index

    def is_indexed(self):
        """Return true if this component is indexed"""
        return UnindexedComponent_set != self._index

    def dim(self):
        """Return the dimension of the index"""
        if UnindexedComponent_set != self._index:
            return self._index.dimen
        else:
            return 0

    def set_value(self, value):
        if UnindexedComponent_set != self._index:
            raise ValueError(
                "Cannot set the value for the indexed component '%s' "
                "without specifying an index value.\n"
                "\tFor example, model.%s[i] = value"
                % (self.name, self.name))
        else:
            raise NotImplementedError(
                "Derived component %s failed to define set_value() "
                "for singleton instances.\n"
                "\tPlease report this to the Pyomo developers"
                % (self.__class__.__name__,))

    # a simple utility to return an id->index dictionary for
    # all composite ComponentData instances.
    def id_index_map(self):
        result = dict()
        for index, component_data in iteritems(self):
            result[id(component_data)] = index
        return result

class ActiveSparseIndexedComponent(SparseIndexedComponent):
    """
    This is the base class for all indexed modeling components
    whose data members are subclasses of ActiveComponentData, e.g.,
    can be activated or deactivated
    """
    def __init__(self, *args, **kwds):
        SparseIndexedComponent.__init__(self, *args, **kwds)

    #
    # Override the base class (de)activate methods
    #

    def activate(self):
        """Set the active attribute to True"""
        Component.activate(self)
        for component_data in itervalues(self):
            component_data._active = True

    def deactivate(self):
        """Set the active attribute to False"""
        Component.deactivate(self)
        for component_data in itervalues(self):
            component_data._active = False

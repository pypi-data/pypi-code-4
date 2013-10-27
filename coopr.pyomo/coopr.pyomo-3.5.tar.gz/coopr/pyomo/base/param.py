#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Param']

import sys
import types
import logging
from weakref import ref as weakref_ref
from six import iteritems, iterkeys, next

from pyutilib.misc import format_io

from coopr.pyomo.base.component import Component, ComponentData, register_component
from coopr.pyomo.base.sparse_indexed_component import SparseIndexedComponent
from coopr.pyomo.base.indexed_component import IndexedComponent, \
    UnindexedComponent_set
from coopr.pyomo.base.misc import apply_indexed_rule, \
    apply_parameterized_indexed_rule, tabular_writer
from coopr.pyomo.base.numvalue import NumericConstant, NumericValue, native_types, value
from coopr.pyomo.base.set_types import Any, Reals

logger = logging.getLogger('coopr.pyomo')

class _ParamData(ComponentData, NumericValue):
    """Holds the numeric value of a mutable parameter"""

    __slots__ = ('value',)

    def __init__(self, owner, value):
        # the following represents an in-lining of the ComponentData
        # constructor call: ComponentData.__init__(self, owner)
        #
        # if owner is None:
        #     self._component = None
        # else:
        #     self._component = weakref_ref(owner)        
        #
        # HOWEVER, as this is a "private" class, and we make sure that
        # owner is never None, we can bypass the check entirely.
        self._component = weakref_ref(owner)        

        # initialize the numeric value-related attributes.
        self.value = value

    def __getstate__(self):
        state = super(_ParamData, self).__getstate__()
        for i in _ParamData.__slots__:
            state[i] = getattr(self, i)
        return state

    # Note: because NONE of the slots on this class need to be edited,
    # we don't need to implement a specialized __setstate__ method, and
    # can quietly rely on the super() class's implementation.
    # def __setstate__(self, state):
    #     pass

    def is_constant(self):
        return False

    def is_fixed(self):
        return True

    def clear(self):
        self.value = None

    def __nonzero__(self):
        """Return True if the value is defined and non-zero."""
        if self.value:
            return True
        if self.value is None:
            raise ValueError("Param: value is undefined")
        return False

    __bool__ = __nonzero__

    def __call__(self, exception=True):
        """Return the value of this object."""
        return self.value


class Param(SparseIndexedComponent):
    """A parameter value, which may be defined over a index"""

    """ Constructor
        Arguments:
           name        The name of this parameter
           index       The index set that defines the distinct parameters.
                         By default, this is None, indicating that there
                         is a single parameter.
           within      A set that defines the type of values that
                         each parameter must be.
           validate    A rule for validating this parameter w.r.t. data
                         that exists in the model
           default     A scalar, rule, or dictionary that defines default 
                         values for this parameter
           initialize  A dictionary or rule for setting up this parameter 
                         with existing model data
           nochecking  If true, various checks regarding valid domain and index
                         values are skipped. Only intended for use by algorithm
                         developers - not modelers!
    """

    DefaultMutable = False

    def __new__(cls, *args, **kwds):
        if cls != Param:
            return super(Param, cls).__new__(cls)
        if args == ():
            return _ParamElement.__new__(_ParamElement)
        else:
            return _ParamArray.__new__(_ParamArray)

    def __init__(self, *args, **kwd):
        self._rule       = kwd.pop('initialize', None )
        self._validate   = kwd.pop('validate', None )
        self.domain      = kwd.pop('within', Any )
        self.nochecking  = kwd.pop('nochecking',False)
        self._mutable    = kwd.pop('mutable', Param.DefaultMutable )
        self._default_val = kwd.pop('default', None )

        if 'repn' in kwd:
            logger.warning(
                "DEPRECATED: The use of the 'repn' keyword when constructing "
                "Params has been deprecated and will be removed in Coopr 4.0.")
            kwd.pop('repn')
        if 'rule' in kwd:
            logger.warning(
                "DEPRECATED: The use of the 'rule' keyword when constructing "
                "Params has been deprecated and will be removed in Coopr 4.0."
                "\n\tPlease use 'initialize'")
            if self._rule is not None:
                raise ValueError(
                    "Cannot specify both initialize and rule parameters when "
                    "constructing a Param object")
            self._rule = self._rule = kwd.pop('rule')

        # "domain=None" should be an alias for domain=Any
        if self.domain is None:
            self.domain = Any

        #
        kwd.setdefault('ctype', Param)
        SparseIndexedComponent.__init__(self, *args, **kwd)

        # Because we want to defer the check for defined values until
        # runtime, we will undo the weakref to ourselves
        if not self.is_indexed():
            del self._data[None]

    def _pprint(self):
        return ( [("Size", len(self)),
                  ("Index", self._index \
                       if self._index != UnindexedComponent_set else None),
                  ("Domain", self.domain.name),
                  ("Default", "(function)" if type(self._default_val) \
                       is types.FunctionType else self._default_val),
                  ("Mutable", self._mutable),
                  ],
                 self.sparse_iteritems(),
                 ( "Key","Value",),
                 lambda k, v: [ k,
                                value(v),
                                ]
                 )

    def Xpprint(self, ostream=None, verbose=False, prefix="   "):
        if ostream is None:
            ostream = sys.stdout
        tab = '    '
        ostream.write(prefix+self.cname()+" : ")
        if self.doc is not None:
            ostream.write(self.doc+'\n'+prefix+tab)
        ostream.write("Size="+str(len(self)))
        if self.domain is not None:
            ostream.write(" Domain="+self.domain.name)
        else:
            ostream.write(" Domain=None")
        if not self._constructed:
            ostream.write("\n"+prefix+tab+"Not constructed\n")
            return

        ostream.write(" Default=")
        if type(self._default_val) is types.FunctionType:
            ostream.write("(function)")
        else:
            ostream.write(str(self._default_val))
        ostream.write(" Mutable="+str(self._mutable))
        ostream.write("\n")
        tabular_writer( ostream, prefix+tab, self.sparse_iteritems(),
                        ("Key","Value"),
                        lambda k,v: [ k, value(v) ] )

    def display(self, prefix="", ostream=None):
        if not self._mutable:
            return
        ostream.write(prefix+"Param "+self.cname()+" :")
        ostream.write(" Size="+str(len(self)))
        ostream.write(" Domain="+self.domain.name+'\n')

        if not self.is_indexed():
            ostream.write("%sValue: %s\n" % (
              prefix, format_io(self[None].value) ))
        else:
            tabular_writer( 
                ostream, prefix, self.sparse_iteritems(), None,
                lambda k, v: [ k, format_io(v.value) ] )
        

    def __len__(self):
        if self._default_val is None:
            return len(self._data)
        return len(self._index)

    def __contains__(self, ndx):
        if self._default_val is None:
            return ndx in self._data
        return ndx in self._index

    def __iter__(self):
        if self._default_val is None:
            return self._data.__iter__()
        return self._index.__iter__()

    #
    # NB: These are "sparse equivalent" access / iteration methods that
    # only loop over the defined data.
    #

    def sparse_keys(self):
        return list(iterkeys(self._data))

    def sparse_values(self):
        return [ self[x] for x in self._data ]

    def sparse_items(self):
        return [ (x, self[x]) for x in self._data ]

    def sparse_iterkeys(self):
        return iterkeys(self._data)

    def sparse_itervalues(self):
        for key in self._data:
            yield self[key]

    def sparse_iteritems(self):
        if not self.is_indexed():
            # this is hackish, and could be improved.
            for key in self._data:
                yield (key, self[key])
        else:
            # when iterating over sparse param values, access the
            # key-value map directly. by definition, the indices are
            # valid, and there is significant overhead associated with
            # the base class __getitem__ method.
            for index, param_value in iteritems(self._data):
                yield (index, param_value)

    # TODO: Not sure what "reset" really means in this context...
    def reset(self):
        pass

    #
    # A utility to extract all index-value pairs defining this
    # parameter, returned as a dictionary. useful in many
    # contexts, in which key iteration and repeated __getitem__
    # calls are too expensive to extract the contents of a parameter.
    #
    def extract_values(self):
        # avoid the use of value() for performance reasons - it is
        # painfully slow in this context.
        if self._mutable:
            ans = {}
            for key, param_value in self.iteritems():
                ans[key] = param_value.value
            return ans
        elif not self.is_indexed():
            return { None: self.value }
        else:
            return dict( self.iteritems() )

    #
    # same as above, but only for defined indices.
    #
    def extract_values_sparse(self):
        # avoid the use of value() for performance reasons - it is
        # painfully slow in this context.
        if self._mutable:
            ans = {}
            for key, param_value in self.sparse_iteritems():
                ans[key] = param_value.value
            return ans
        elif not self.is_indexed():
            return { None: self.value }
        else:
            return dict( self.sparse_iteritems() )

    #
    # takes as input a (index, value) dictionary or a scalar for
    # updating this Param.  if check=True, then both the index and value
    # are checked through the __getitem__ method of this class.
    #
    def store_values(self, new_values, check=True):

        if self._mutable is False:
            raise RuntimeError("Cannot call store_values method of Param="+
                               self.cname(True)+"; parameter is immutable.")

        _srcType = type(new_values)
        _isDict = _srcType is dict or ( \
            hasattr(_srcType, '__getitem__') 
            and not isinstance(new_values, NumericValue) )
        
        if check is True:
            if _isDict:
                for index, new_value in iteritems(new_values):
                    self[index] = new_value
            else:
                for index in self._index:
                    self[index] = new_values
            return

        #
        # WARNING: If check == False, then we bypass almost all of the
        # Param logic for ensuring data integrity.  It should ONLY be
        # set by developers!
        #

        if self.is_indexed():
            if _isDict:
                # It is possible that the Param is sparse and that the
                # index is not already in the _data dict.  As these
                # cases are rare, we will recover from the exception
                # instead of incurring the penalty of checking.
                for index, new_value in iteritems(new_values):
                    try:
                        self._data[index].value = new_value
                    except:
                        self._data[index] = _ParamData(self, new_value)
            else:
                # For scalars, we will choose an approach based on
                # how "dense" the Param is
                if not self._data: # empty
                    for index in self._index:
                        self._data[index] = _ParamData(self, new_values)
                elif len(self._data) == len(self._index):
                    for index in self._index:
                        self._data[index].value = new_values
                else:
                    for index in self._index:
                        if index in self._data:
                            self._data[index].value = new_values
                        else:
                            self._data[index] = _ParamData(self, new_values)
        else:
            if _isDict:
                if None not in new_values:
                    raise RuntimeError(
                        "Cannot store value for singleton Param="+
                        self.cname(True)+"; no value with index None "
                        "in input new values map.")
                new_values = new_values[None]
            # singletons have to be handled differently
            self[None].value = new_values
            self._data[None] = None


    def _default(self, idx):
        # FIXME: Ideally, we should test for using an unconstructed
        # Param; however, actually enforcing this breaks lots & lots of
        # tests...
        #        
        #if not self._constructed:
        #    if idx is None:
        #        idx_str = '%s' % (self.name,)
        #    else:
        #        idx_str = '%s[%s]' % (self.name, idx,)
        #    raise ValueError(
        #        "Error retrieving Param value (%s): The Param value has "
        #        "not been constructed" % ( idx_str,) )                
        #
        # FIXME: Ideally, a key miss should raise a KeyError; however,
        # for mostly historical reasons, Pyomo has raised a ValueError
        # (the logic being that all indices used to be defined at
        # construction, so a key miss was the result of a bad value).
        # Changing this to a KeyError generates numerous test failures, so
        # when someone has time to track down and fix those errors, we
        # SHOULD change the exception to KeyError.
        #
        _check_value_domain = True

        val = self._default_val
        _default_type = type(self._default_val)

        if val is None:
            if self.is_indexed():
                idx_str = '%s[%s]' % (self.cname(True), idx,)
            else:
                idx_str = '%s' % (self.cname(True),)
                raise ValueError(
                    "Error retrieving Param value (%s): The Param value is "
                    "undefined and no default value is specified"
                    % ( idx_str,) )
        elif _default_type in native_types:
            # Native types are static, and the set_default() method
            # takes care of validating the domain, so we can skip that
            # logic here.  This actually covers most of the common use cases.
            _check_value_domain = False
        elif _default_type is types.FunctionType:
            val = apply_indexed_rule(self, val, self.parent(), idx)
        elif hasattr(val, '__getitem__') and not isinstance(val, NumericValue):
            val = val[idx]
        else:
            pass

        if _check_value_domain:
            if val.__class__ not in native_types:
                if isinstance(val, NumericValue):
                    val = val()
            
            if val not in self.domain:
                raise ValueError(
                    "Invalid default parameter value: %s[%s] = '%s';"
                    " value type=%s.\n\tValue not in parameter domain %s" %
                    (self.cname(True), idx, val, type(val), self.domain.name) )
        
        if self._mutable:
            # While slightly less efficient, calling __setitem__ ensures
            # that the parameter validation routine gets called in a
            # consistent manner.
            if idx is None:
                self._raw_setitem(idx, val)
            else:
                self._raw_setitem(idx, _ParamData(self, val), True)
            return self[idx]
        else:
            # This is kludgy: If the user wants to validate the Param
            # values, we need to validate the default value as well.
            # For Mutable Params, this is easy: setitem will inject the
            # value into _data and then call validate.  For immutable
            # params, we never inject the default into the data
            # dictionary.  This will break validation, as the validation
            # rule is allowed to assume the data is already present
            # (actually, it will die on infinite recursion, as
            # Param.__getitem__() will re-call _default).
            #
            # So, we will do something very inefficient: if we are
            # validating, we will inject the value into the dictionary,
            # call validate, and remove it.
            if self._validate:
                try:
                    self._data[idx] = val
                    self._raw_validateitem(idx, val)
                finally:
                    del self._data[idx]
            return val


    def set_default(self, val):
        if self._constructed \
                and val is not None \
                and type(val) in native_types \
                and val not in self.domain:
            raise ValueError(
                "Default value (%s) is not valid for Param domain %s" %
                ( str(val), self.domain.name ) )
        self._default_val = val

    # the default may be None, indicating unassigned. it may also be a function,
    # used to assign default values to specific indices.
    def default(self):
        return self._default_val

    # the __setitem__ method below performs significant validation around
    # the input indices, and processing / conversion of values. in various
    # contexts, we don't need to incur this overhead, specifically during
    # initialization. assumes the input value is in the set native_types
    #
    # NOTE: the ndx CANNOT be in self._data if _new_indexed_value_ok == True
    # (this would break any expressions that held a reference to
    # the old ParamData)
    def _raw_setitem(self, ndx, val, _new_indexed_value_ok=False):
        if _new_indexed_value_ok:
            self._data[ndx] = val
        else:
            # Params should contain *values*.  Normally, I would just call
            # value(), but that forces the value to be a /numeric value/,
            # which for historical reasons, we have not forced.  Notably, we
            # have allowed Params with domain==Any to hold strings, tuples,
            # etc.  The following lets us use NumericValues to initialize
            # Params, but is optimized to check for "known" native types to
            # bypass a potentially expensive isinstance()==False call.
            #
            if val.__class__ not in native_types:
                if isinstance(val, NumericValue):
                    val = val()

            if val not in self.domain:
                raise ValueError(
                    "Invalid parameter value: %s[%s] = '%s', value type=%s.\n"
                    "\tValue not in parameter domain %s" %
                    (self.cname(True), ndx, val, type(val), self.domain.name) )

            if ndx is None:
                self.value = val
                self._data[None] = None

            elif self._mutable:
                if ndx in self._data:
                    self._data[ndx].value = val
                else:
                    self._data[ndx] = _ParamData(self, val)

            else:
                self._data[ndx] = val

        if self._validate:
            self._raw_validateitem(ndx, val)

    # perform validation of the given input/value pair.
    def _raw_validateitem(self, ndx, val):

        if self.is_indexed():
            if type(ndx) is tuple:
                tmp = ndx
            else:
                tmp = (ndx,)
        else:
            tmp = ()
        if not apply_parameterized_indexed_rule(
            self, self._validate, self.parent(), val, tmp ):
            raise ValueError(
                "Invalid parameter value: %s[%s] = '%s', value type=%s.\n"
                "\tValue failed parameter validation rule" %
                ( self.cname(True), ndx, val, type(val) ) )

    def __setitem__(self, ndx, val):
        if self._constructed and not self._mutable:
            raise TypeError(
"""Attempting to set the value of the immutable parameter %s after the
parameter has been constructed.  If you intend to change the value of
this parameter dynamically, please declare the parameter as mutable
[i.e., Param(mutable=True)]""" % (self.cname(True),))

        #
        # Validate the index
        #

        #
        # TBD: Potential optimization: if we find that updating a Param is
        # more common than setting it in the first place, then first
        # checking the _data and then falling back on the _index *might*
        # be more efficient.
        #
        if ndx not in self._index:
            # We rely (for performance purposes) on "most" people doing
            # things correctly; that is, they send us either a scalar or
            # a valid tuple.  So, for efficiency, we will check the
            # index *first*, and only go through the hassle of
            # flattening things if the ndx is not found.
            ndx = self.normalize_index(ndx)
            if ndx not in self._index:
                if not self.is_indexed():
                    msg = "Error setting parameter value: " \
                          "Cannot treat the scalar Param '%s' as an array" \
                          % ( self.cname(True), )
                else:
                    msg = "Error setting parameter value: " \
                          "Index '%s' is not valid for array Param '%s'" \
                          % ( ndx, self.cname(True), )
                raise KeyError(msg)

        # we have a valid index and value - do the actual set.
        self._raw_setitem(ndx, val)

    def _initialize_from(self, _init):
        _init_type = type(_init)
        _isDict = _init_type is dict

        if _isDict or _init_type in native_types:
            # Dicts / constants are the most comm
            pass
        elif _init_type is types.FunctionType:
            if not self.is_indexed():
                self[None] = _init(self.parent())
                # We are Done... bypass further processing
                return
            else:
                self_parent = self.parent()

                # A situation can arise in which the parameter is
                # indexed by an empty set, or an empty set tuple. 
                # Rare, but it has happened.
                try: #if len(self._index) != 0: 
                    _iter = self._index.__iter__()
                    idx = next(_iter)
                    val = apply_indexed_rule(self, _init, self_parent, idx)

                    # We want to allow rules that return a dict (or
                    # dict-like thing) to behave as if the dict was
                    # provided to the constructor's "initialize="
                    # argument.  The simplest (and cleanest - no
                    # duplicated code) way to do that is to allow for
                    # recursion
                    if hasattr(val, '__getitem__') \
                            and not isinstance(_init, NumericValue):
                        try:
                            self._initialize_from(val)
                            return
                        except:
                            pass

                    # At this point, we know the value is specific to
                    # this index (i.e., not likely to be a dict-like
                    # thing), and that the index is valid; so, it is
                    # safe to use _raw_setitem (which will perform all
                    # the domain / validation checking)
                    self._raw_setitem(idx, val)
                        
                    # IMPORTANT: We assume that the iterator over an
                    #    index set returns a flattened tuple. Otherwise,
                    #    the validation process is far too expensive.
                    for idx in _iter:
                        self._raw_setitem(
                            idx, apply_indexed_rule(
                                self, _init, self_parent, idx ) )
                    # We are Done... bypass further processing
                    return
                except StopIteration:
                    # The index set was empty...
                    pass
        elif isinstance(_init, NumericValue):
            # Reduce NumericValues to scalars.  This is implortant so
            # that singleton components are treated as numbers and not
            # as indexed components with a index set of [None]
            _init = _init()
        elif isinstance(_init, SparseIndexedComponent):
            # Ideally, we want to reduce SparseIndexedComponents to
            # a dict, but without "densifying" it.  However, since
            # there is no way to (easily) get the default value, we
            # will take the "less surprising" route of letting the
            # source become dense, so that we get the expected copy.
            sparse_src = len(_init) != len(_init.keys())
            tmp = dict( _init.iteritems() )
            if sparse_src and len(_init) == len(_init.keys()):
                logger.warning("""
Initializing Param %s using a sparse mutable indexed component (%s).
This has resulted in the conversion of the source to dense form.
""" % ( self.cname(True), _init.name ) )
            _init = tmp
            _isDict = True
        elif isinstance(_init, IndexedComponent):
            # FIXME: is there a general form for IndexedComponent, or
            # should we just wait until everything moves over to
            # SparseIndexedComponents?  Right now, we will treat them as
            # simple dictionaries
            _isDict = True
            pass

        # if the _init is not a native dictionary, but it
        # behaves like one (that is, it could be converted to a
        # dict with "dict((key,_init[key]) for key in _init)"),
        # then we will treat it as such
        if not _isDict and hasattr(_init, '__getitem__'):
            try:
                _isDict = True
                for x in _init:
                    _init.__getitem__(x)
            except:
                _isDict = False

        if _isDict:
            # Because this is a user-specified dictionary, we
            # must use the normal (expensive) __setitem__ route
            # so that the individual indices are validated.
            for key in _init:
                self[key] = _init[key]
        else:
            try: #if len(self._index) != 0:
                # the following is optimized, due to its frequent
                # occurence in practice. which may sound weird, in
                # that a constant is being supplied as a default to
                # an indexed parameter - but it does happen,
                # particularly when dealing with mutable
                # parameters. failing to perform these optimizations
                # unnecessarily blows up run times, on a number of
                # large-scale models.
                
                # Note: because there is a single value, we only
                # need to validate the value against the domain
                # once.
                _iter = self._index.__iter__()
                idx = next(_iter)
                self._raw_setitem(idx, _init)

                # Note: the following is safe for both indexed and
                # non-indexed parameters: for non-indexed, the first
                # idx (above) will be None, and the for-loop below
                # will NOT be called.
                if self._mutable:
                    _init = self[idx].value
                    for idx in _iter:
                        self._raw_setitem( idx, _ParamData(self,_init), True )
                else:
                    _init = self[idx]
                    for idx in _iter:
                        self._raw_setitem(idx, _init, True)
            except StopIteration:
                # The index set was empty...
                pass


    def construct(self, data=None):
        """ Apply the rule to construct values in this set """

        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Param, name=%s, from data=%s"
                             % ( self.cname(True), str(data) ))

        if self._constructed:
            raise IOError(
                "Cannot reconstruct parameter '%s' (already constructed)"
                % self.cname(True) )
            return

        self.clear()

        #
        # Construct using the initial data or the data loaded from an
        # external source. Data values will be queried in to following
        # order:
        #   1) the 'data' dictionary
        #   2) the self._rule dictionary or rule
        #   3) [implicit: fall back on the default value]
        #
        # To accomplish this, we will first set all the values based on
        # self._rule, and then allow the data dictionary to
        # overwrite anything.
        #
        # NB: Singleton Params can always be treated as "normal" indexed
        # params, indexed by a set {None}.
        #
        # NB: Previously, we would raise an exception for constructing
        # scalar parameters with no defined data.  As that was a special
        # case (i.e. didn't apply to arrays) and was frustrating for
        # Concrete folks who were going to initialize the value later,
        # we will allow an undefined Param to be constructed and will
        # instead throw an exception later if the user tries to *use* the
        # Param before it is initialized.
        #

        # Step #1: initialize everything from the Rule
        if self._rule is not None:
            self._initialize_from(self._rule)

        # Step #2: allow any user-specified (external) data to override
        # the initialization
        if data is not None:
            try:
                for key, val in iteritems(data):
                    self[key] = val
            except Exception:
                msg = sys.exc_info()[1]
                if type(data) is not dict:
                   raise ValueError(
                       "Attempting to initialize parameter=%s with data=%s.\n"
                       "\tData type is not a dictionary, and a dictionary is "
                       "expected. Did you create a dictionary with a \"None\" "
                       "index?" % (self.cname(True), str(data)) )
                else:
                    raise RuntimeError(
                        "Failed to set value for param=%s, index=%s, value=%s."
                        "\n\tsource error message=%s" 
                        % (self.cname(True), str(key), str(val), str(msg)) )

        self._constructed = True

        # If the default value is a simple type, we can check it versus
        # the domain (now that the domain is constructed) and save some
        # time later on
        self.set_default(self._default_val)

    #
    # reconstruction for a parameter is particularly useful for cases where
    # an initialize rule is provided. these rules typically return an atomic
    # value, which in turn may be a function of other parameters. one would
    # like reconstruction when the values of those dependent parameters change.
    # 
    # IMPT: Only mutable parameters can be reconstructed - otherwise, the 
    #       construction wouldn't "take", e.g., the changes would not be 
    #       propagated to any referencing constraints.
    #    
    def reconstruct(self, data=None):

        if self._mutable is False:
            raise RuntimeError("Cannot invoke reconstruct method of immutable param="+self.cname(True))

        SparseIndexedComponent.reconstruct(self, data=data)

    #
    # a simple utility to set all of the data elements in the 
    # index set of this parameter to the common input value.
    # if the entries are there, it will over-ride the values.
    # if the entries are not there, it will create them.
    #
    def initialize_all_to(self, common_value):
        logger.warning(
            "DEPRECATED: Param.initialize_all_to().  "
            "Please use Param.store_values(common_value).  "
            "This method will be removed in Coopr 4.0." )
        return self.store_values(common_value, check=False)


class _ParamElement(_ParamData, Param):

    def __init__(self, *args, **kwds):
        Param.__init__(self, *args, **kwds)
        _ParamData.__init__(self, self, kwds.get('default',None))

    # Since this class derives from Component and Component.__getstate__
    # just packs up the entire __dict__ into the state dict, there s
    # nothng special that we need to do here.  We will just defer to the
    # super() get/set state.  Since all of our get/set state methods
    # rely on super() to traverse the MRO, this will automatically pick
    # up both the Component and Data base classes.
    #
    #def __getstate__(self):
    #    pass
    #
    #def __setstate__(self, state):
    #    pass

    def __call__(self, *args, **kwds):

        if not self._constructed is True:
            raise ValueError(
                "Param %s has not been construced" % self.cname(True) )

        # Needed because we rely on self[None] to know if this parameter
        # is valid.  In particular, if we are getting data from the
        # default value, calling self[None] will actually inject the
        # [None] entry into _data.
        ans = self[None]
        if None in self._data:
            return _ParamData.__call__(self, *args, **kwds)
        else:
            return ans

    def set_value(self, value):
        if self._constructed and not self._mutable:
            raise TypeError(
"""Attempting to set the value of the immutable parameter %s after the
parameter has been constructed.  If you intend to change the value of
this parameter dynamically, please declare the parameter as mutable
[i.e., Param(mutable=True)]""" % (self.cname(True),))
        self[None] = value
        
    def is_constant(self):
        return self._constructed and not self._mutable


class _ParamArray(Param):
    pass


register_component(Param, "Parameter data that is used to define a model instance.")


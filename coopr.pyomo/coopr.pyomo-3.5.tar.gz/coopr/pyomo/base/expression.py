#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Expression', '_ExpressionData']

import sys
import types
import logging
from six import iteritems, iterkeys, next

from coopr.pyomo.base.component import ComponentData, register_component
from coopr.pyomo.base.sparse_indexed_component import SparseIndexedComponent
from coopr.pyomo.base.indexed_component import IndexedComponent, UnindexedComponent_set
from coopr.pyomo.base.misc import apply_indexed_rule, apply_parameterized_indexed_rule, \
     create_name
from coopr.pyomo.base.numvalue import NumericConstant, NumericValue, native_types, value, as_numeric
import coopr.pyomo.base.expr

logger = logging.getLogger('coopr.pyomo')

# TODO: Rename to _ExpressionData
class _ExpressionData(ComponentData, NumericValue):
    """An object that defines an expression that is never cloned"""

    __slots__ = ('_value',)

    # We make value a property so we can ensure that the value
    # assigned to this component is numeric and that all uses of 
    # .value on the NumericValue base class will work
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if value is not None:
            self._value = as_numeric(value)
        else:
            self._value = None

    # TODO: Remove
    def assign(self, value):
        self.value = value

    def __init__(self, owner, value):
        """Constructor"""
        ComponentData.__init__(self, owner)
        self.value = value

    def __getstate__(self):
        state = super(_ExpressionData, self).__getstate__()
        for i in _ExpressionData.__slots__:
            state[i] = getattr(self, i)
        return state

    # Note: because NONE of the slots on this class need to be edited,
    # we don't need to implement a specialized __setstate__ method, and
    # can quietly rely on the super() class's implementation.
    # def __setstate__(self, state):
    #     pass

    def is_constant(self):
        # The underlying expression can always be changed
        # so this should never evaluate as constant
        return False

    def is_fixed(self):        
        return self._value.is_fixed()

    def __call__(self, exception=True):
        """Return the value of this object."""
        return self._value()

    #################
    # Methods which mock _ExpressionBase behavior defined below
    #################

    # Note: using False here COULD potentially improve performance inside
    #       expression generation and means we wouldn't need to define a (no-op) clone
    #       method. However, there are TONS of places throughout the code base where
    #       is_expression is used to check whether one needs to "dive deeper" into the _args
    def is_expression(self):
        return True

    @property
    def _args(self):
        return (self._value,)

    def clone(self):
        return self

    def polynomial_degree(self):
        return self._value.polynomial_degree()

    def to_string(self, ostream=None, verbose=None, precedence=0):
        if ostream is None:
            ostream = sys.stdout
        _verbose = coopr.pyomo.base.expr.TO_STRING_VERBOSE if \
            verbose is None else verbose
        if _verbose:
            ostream.write(str(self))
            ostream.write("{")
        if self._value is None:
            ostream.write("Undefined")
        else:# self._value.is_expression():
            self._value.to_string( ostream=ostream, verbose=verbose, 
                                   precedence=precedence ) 
        #else:
        #    ostream.write(str(self._value))
        if _verbose:
            ostream.write("}")


class Expression(SparseIndexedComponent):
    """A shared expression container, which may be defined over a index"""

    """ Constructor
        Arguments:
           name        The name of this expression
           index       The index set that defines the distinct expression.
                         By default, this is None, indicating that there
                         is a single expression.
           default     A scalar, rule, or dictionary that defines default 
                         values for this expression
           initialize  A dictionary or rule for setting up this expression 
                         with existing model data
    """

    def __new__(cls, *args, **kwds):
        if cls != Expression:
            return super(Expression, cls).__new__(cls)
        if args == ():
            return _ExpressionElement.__new__(_ExpressionElement)
        else:
            return _ExpressionArray.__new__(_ExpressionArray)

    def __init__(self, *args, **kwd):
        self._rule       = kwd.pop('initialize', None )

        if 'rule' in kwd:
            logger.warning(
                "DEPRECATED: The use of the 'rule' keyword when constructing "
                "Expressions has been deprecated and will be removed in Coopr 4.0."
                "\n\tPlease use 'initialize'")
            if self._rule is not None:
                raise ValueError(
                    "Cannot specify both initialize and rule parameters when "
                    "constructing a Expression object")
            self._rule = self._rule = kwd.pop('rule')

        self._default_val = None
        default = kwd.pop('default', None )
        
        kwd.setdefault('ctype', Expression)
        SparseIndexedComponent.__init__(self, *args, **kwd)

        self.set_default(default)

        # Because we want to defer the check for defined values until
        # runtime, we will undo the weakref to ourselves
        if not self.is_indexed():
            del self._data[None]

    def _pprint(self):
        return (
            [('Size', len(self)),
             ('Index', None if self._index is UnindexedComponent_set \
                  else self._index),
             ("Default", "(function)" if type(self._default_val) \
                  is types.FunctionType else self._default_val),
             ],
            self.sparse_iteritems(),
            ("Key","Expression"),
            lambda k,v: [ k, 
                          "Undefined" if v.value is None else v.value
                          ]
            )

    def Xpprint(self, ostream=None, verbose=None, precedence=0):
        if ostream is None:
            ostream = sys.stdout
        ostream.write("   %s : " % (self.cname(True),))
        if self.doc is not None:
            ostream.write(" %s\n   " % (self.doc,))
        ostream.write("\tSize=%s\n"
                       % (len(self)) )
        if not self._constructed:
            ostream.write("\tNot constructed\n")
        elif None in self.keys():
            if None in self._data:
                if self[None].value is None:
                    ostream.write("\t%s\n" % None)
                elif self[None].value.is_expression():
                    ostream.write("\t")
                    self[None].value.pprint(ostream=ostream)
                else:
                    ostream.write("\t")
                    self[None].value.pprint(ostream=ostream)
                    ostream.write("\n")
            else:
                ostream.write("\tUndefined\n")
        else:
            for key, val in sorted(self.sparse_iteritems()):
                if val.value is None:
                    ostream.write("\t%s : %s\n" % (key, None))
                elif val.value.is_expression():
                    ostream.write("\t%s : " % key)
                    val.value.pprint(ostream=ostream)
                else:
                    ostream.write("\t%s : " % key)
                    val.value.pprint(ostream=ostream)
                    ostream.write("\n")                    

        if self._default_val is not None:
            ostream.write("\tdefault: ")
            if type(self._default_val) is types.FunctionType:
                ostream.write("(function)\n")
            else:
                ostream.write("%s\n" % self._default_val)

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
            # when iterating over sparse values, access the key-value map directly. by
            # definition, the indices are valid, and there is significant overhead associated
            # with the base class __getitem__ method.
            for index, value in iteritems(self._data):
                yield (index, value)

    # TODO: Not sure what "reset" really means in this context...
    def reset(self):
        pass

    #
    # A utility to extract all index-value pairs defining this
    # expression, returned as a dictionary. useful in many
    # contexts, in which key iteration and repeated __getitem__
    # calls are too expensive to extract the contents of an expression.
    #
    def extract_values(self):
        return dict((key, expression_data.value) for key, expression_data in iteritems(self))

    #
    # same as above, but only for defined indices.
    #
    def extract_values_sparse(self):
        if not self.is_indexed():
            return dict((key, expression_data.value) for key, expression_data in self.sparse_iteritems())
        else:
            return dict((key, expression_data.value) for key, expression_data in iteritems(self._data))
            
    #
    # takes as input a (index, value) dictionary for updating this Expression.
    # if check=True, then both the index and value are checked through 
    # the __getitem__ method of this class. 
    #
    def store_values(self, new_values):

        if (self.is_indexed() is False) and (not None in new_values):
            raise RuntimeError("Cannot store value for singleton Expression="+self.cname(True)+"; no value with index None in input new values map.")

        if self.is_indexed():
            for index, new_value in iteritems(new_values):
                self._data[index].value = new_value
        else:
            # singletons have to be handled differently
            self[None].value = new_values[None]

    def _default(self, idx):

        if not self._constructed:
            if idx is None:
                idx_str = '%s' % (self.cname(True),)
            else:
                idx_str = '%s[%s]' % (self.cname(True), idx,)
            raise ValueError(
                "Error retrieving Expression value (%s): The Expression value has "
                "not been constructed" % ( idx_str,) )                
 
        if self._default_val is None:
            if idx is None:
                idx_str = '%s' % (self.cname(True),)
            else:
                idx_str = '%s[%s]' % (self.cname(True), idx,)
            raise KeyError(
                "Error retrieving Expression value (%s): The Expression value is "
                "undefined and no default value is specified"
                % ( idx_str,) )

        _default_type = type(self._default_val)
        if _default_type in native_types:
            val = self._default_val
        elif _default_type is types.FunctionType:
            val = apply_indexed_rule(
                self, self._default_val, self.parent(), idx )
        elif hasattr(self._default_val, '__getitem__'):
            try:
                val = self._default_val[idx]
            except IndexError:
                val = self._default_val
        else:
            val = self._default_val

        self[idx] = val
        return val

    def set_default(self, val):
        self._default_val = val

    # the __setitem__ method below performs significant validation around
    # the input indices, and processing / conversion of values. in various
    # contexts, we don't need to incur this overhead, specifically during
    # initialization. assumes the input value is in the set native_types
    def _raw_setitem(self, ndx, val):

        if ndx is None:
            self.value = val
            self._data[ndx] = None
        elif ndx in self._data:
            self._data[ndx].value = val
        else:
            self._data[ndx] = _ExpressionData(self, val)

    def __setitem__(self, ndx, val):
        

        if ndx not in self._index:

            # We rely (for performance purposes) on "most" people doing things 
            # correctly; that is, they send us either a scalar or a valid tuple.  
            # So, for efficiency, we will check the index *first*, and only go
            # through the hassle of flattening things if the ndx is not found.
            ndx = self.normalize_index(ndx)
            if ndx not in self._index:
                if not self.is_indexed():
                    msg = "Error setting Expression value: " \
                          "Cannot treat the scalar Expression '%s' as an array" \
                          % ( self.cname(True), )
                else:
                    msg = "Error setting Expression value: " \
                          "Index '%s' is not valid for array Expression '%s'" \
                          % ( ndx, self.cname(True), )
                raise KeyError(msg)

        # we have a valid index and value - do the actual set.
        self._raw_setitem(ndx, val)

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """

        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Expression, name=%s, from data=%s"
                             % ( self.cname(True), str(data) ))

        if self._constructed:
            raise IOError(
                "Cannot reconstruct Expression '%s' (already constructed)"
                % self.cname(True) )
            return

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
        # NB: Singleton Expressions can always be treated as "normal" indexed
        # expression, indexed by a set {None}.
        #
        #
        # NB: Previously, we would raise an exception for constructing
        # scalar Expressions with no defined data.  As that was a special
        # case (i.e. didn't apply to arrays) and was frustrating for
        # Concrete folks who were going to initialize the value later,
        # we will allow an undefined Expression to be constructed and will
        # instead throw an exception later if the user tries to *use* the
        # Expression before it is initialized.
        #
        _init = self._rule
        if _init is not None:
            _init_type = type(_init)
            if _init_type is dict:
                for key, val in iteritems(_init):
                    self[key] = val
            elif _init_type is types.FunctionType:
                if self.is_indexed():
                    # a situation can arise in which the expression is indexed by
                    # an empty set, or an empty set tuple. rare, but it has happened.
                    if len(self._index) != 0: 
                        _iter = self._index.__iter__()
                        idx = next(_iter)
                        val = apply_indexed_rule(self, _init, self.parent(), idx)
                        if type(val) is dict:
                            for key, v in iteritems(val):
                                self[key] = v
                        else:
                            # the following is optimized, due to its frequent occurence
                            # in practice. failing to perform these optimizations
                            # unnecessarily blows up run times, on a number of large-scale
                            # models.

                            self_parent = self.parent()

                            for idx in self._index:

                                # IMPORTANT: We assume that the iterator over an index
                                #            set returns a flattened tuple. Otherwise,
                                #            the validation process is far too expensive.

                                val = apply_indexed_rule(self, _init, self_parent, idx)

                                # At this point, we know _init is a raw native 
                                # type value, or one that can be treated as such. 
                                # we have a valid index and value - set it.
                                self._raw_setitem(idx, val)

                else:
                    self[None] = _init(self.parent())
            else:
                if isinstance(_init, SparseIndexedComponent):
                    # Ideally, we want to reduce SparseIndexedComponents
                    # to a dict, but without "densifying" it.  However,
                    # since there is no way to (easily) get the default
                    # value, we will take the "less surprising" route of
                    # letting the source become dense, so that we get
                    # the expected copy.
                    sparse_src = len(_init) != len(_init.keys())
                    tmp = {}
                    for key in _init.keys():
                        try:
                            val = _init[key]
                        except ValueError:
                            continue
                        tmp[key] = val
                    tmp = dict(iteritems(_init))
                    if sparse_src and len(_init) == len(_init.keys()):
                        logger.warning("""
Initializing Expression %s using a sparse mutable indexed component (%s).
    This has resulted in the conversion of the source to dense form.
""" % ( self.cname(True), _init.name ) )
                    _init = tmp
                elif isinstance(_init, IndexedComponent):
                    # FIXME: is there a general form for
                    # IndexedComponent, or should we just wait until
                    # everything moves over to SparseIndexedComponents?
                    pass

                # if things look like a dictionary, then we will treat
                # it as such
                _isDict = hasattr(_init, '__getitem__')
                if _isDict:
                    try:
                        for x in _init:
                            _init.__getitem__(x)
                    except:
                        _isDict = False
                if _isDict:
                    for key in _init:
                        self[key] = _init[key]
                else:
                    # the following is optimized, due to its frequent occurence
                    # in practice. failing to perform these optimizations
                    # unnecessarily blows up run times, on a number of large-scale
                    # models.
                    for key in self._index:

                        # IMPORTANT: We assume that the iterator over an index
                        #            set returns a flattened tuple. Otherwise,
                        #            the validation process is far too expensive.

                        # At this point, we know _init is a raw native type
                        # value, or one that can be treated as such. 
                        # we have a valid index and value - set it.
                        self._raw_setitem(key, _init)


        if data is not None:
            try:
                for key, val in iteritems(data):
                    self[key] = val
            except Exception:
                msg = sys.exc_info()[1]
                if type(data) not in [dict]:
                   raise ValueError("Attempting to initialize Expression="+self.cname(True)+" with data="+str(data)+". Data type is not a dictionary, and a dictionary is expected. Did you create a dictionary with a \"None\" index?")
                else:
                    raise RuntimeError("Failed to set value for Expression="+self.cname(True)+", index="+str(key)+", value="+str(val)+"; source error message="+str(msg))

        self._constructed = True
        self.set_default(self._default_val)


    #
    # a simple utility to set all of the data elements in the 
    # index set of this expression to the common input value.
    # if the entries are there, it will over-ride the values.
    # if the entries are not there, it will create them.
    #
    def initialize_all_to(self, common_value):

        if self.is_indexed():
            for index in self._index:
                self._data[index] = _ExpressionData(self, common_value)
        else:
            self[None] = common_value

class _ExpressionElement(_ExpressionData, Expression):

    def __init__(self, *args, **kwds):
        Expression.__init__(self, *args, **kwds)
        _ExpressionData.__init__(self, self, kwds.get('default',None))

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

    def Xpprint(self, ostream=None, verbose=None, nested=False, eol_flag=True, precedence=0):
        # Needed so that users find Expression.pprint and not _ExpressionData.pprint
        if precedence == 0:
            Expression.pprint(self, ostream=ostream, verbose=None)
        else:
            ostream.write(str(self))

    def __call__(self, *args, **kwds):

        if not self._constructed is True:
            raise ValueError("Expression %s has not been construced" % self.cname(True))

        # Needed because we rely on self[None] to know if this expression
        # is valid.  In particular, if we are getting data from the
        # default value, calling self[None] will actually inject the
        # [None] entry into _data.
        ans = self[None]
        if None in self._data:
            return _ExpressionData.__call__(self, *args, **kwds)
        else:
            return value(ans)

    def set_value(self, value):
        self[None] = value
        

class _ExpressionArray(Expression):

    def __init__(self, *args, **kwds):
        Expression.__init__(self, *args, **kwds)

    def display(self, ostream=None):
        self.pprint(ostream=ostream)


register_component(Expression, "A container for shared expression data.")


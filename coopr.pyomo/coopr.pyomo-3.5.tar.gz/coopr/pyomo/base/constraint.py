#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Constraint', '_ConstraintData', 'ConstraintList', 
           'simple_constraint_rule', 'simple_constraintlist_rule']

import sys
import logging
from weakref import ref as weakref_ref

from inspect import isgenerator

from six import StringIO, iteritems

import pyutilib.math
import pyutilib.misc

from coopr.pyomo.base.expr import _ExpressionBase, _EqualityExpression, \
    generate_relational_expression, generate_expression_bypassCloneCheck
from coopr.pyomo.base.numvalue import ZeroConstant, value, as_numeric, _sub
from coopr.pyomo.base.component import ActiveComponentData, register_component
from coopr.pyomo.base.indexed_component import ActiveIndexedComponent, UnindexedComponent_set
from coopr.pyomo.base.misc import apply_indexed_rule, tabular_writer
from coopr.pyomo.base.sets import Set

logger = logging.getLogger('coopr.pyomo')

_simple_constraint_rule_types = set([ type(None), bool ])


def simple_constraint_rule( fn ):
    """This is a decorator that translates None/True/False return values
    into Constraint.Skip/Constraint.Feasible/Constraint.Infeasible.
    This supports a simpler syntax in constraint rules, though these can be
    more difficult to debug when errors occur.

    Example use:

    @simple_constraint_rule
    def C_rule(model, i, j):
        ...
    """
    def wrapper_function ( *args, **kwargs ):
        if fn.__class__ in _simple_constraint_rule_types:
            value = fn
        else:
            value = fn( *args, **kwargs )
        if value.__class__ in _simple_constraint_rule_types:
            if value is None:
                return Constraint.Skip
            elif value is True:
                return Constraint.Feasible
            elif value is False:
                return Constraint.Infeasible
        return value
    return wrapper_function


def simple_constraintlist_rule( fn ):
    """This is a decorator that translates None/True/False return values
    into ConstraintList.End/Constraint.Feasible/Constraint.Infeasible.
    This supports a simpler syntax in constraint rules, though these can be
    more difficult to debug when errors occur.

    Example use:

    @simple_constraintlist_rule
    def C_rule(model, i, j):
        ...
    """
    def wrapper_function ( *args, **kwargs ):
        if fn.__class__ in _simple_constraint_rule_types:
            value = fn
        else:
            value = fn( *args, **kwargs )
        if value.__class__ in _simple_constraint_rule_types:
            if value is None:
                return ConstraintList.End
            elif value is True:
                return Constraint.Feasible
            elif value is False:
                return Constraint.Infeasible
        return value
    return wrapper_function



class _ConstraintData(ActiveComponentData):
    """
    This class defines the data for a single constraint.

    Constructor arguments:
        component       The Constraint object that owns this data.

    Public class attributes:
        active          A boolean that is true if this constraint is active in the model.
        component       The constraint component.
        body            The Pyomo expression for this constraint
        lower           The Pyomo expression for the lower bound
        upper           The Pyomo expression for the upper bound
    """

    __pickle_slots__ = ( 'body', 'lower', 'upper', '_equality')
    __slots__ = __pickle_slots__ + ( '__weakref__', )

    def __init__(self, owner):

        # the following lines represent in-lining of the ActiveComponentData
        # and ComponentData constructors. The only difference is that we do
        # not need to check for owner == None - this is a private class, and
        # the constructor should never be called with no owner.
        self._component = weakref_ref(owner)
        self._active = True

        # initialize the remaining class slots

        self.body = None # an expression tree encoding

        self.lower = None
        self.upper = None
        self._equality = False

    def __getstate__(self):
        """
        This method must be defined because this class uses slots.
        """
        result = super(_ConstraintData, self).__getstate__()
        for i in _ConstraintData.__pickle_slots__:
            result[i] = getattr(self, i)
        return result

    # Since this class requires no special processing of the state
    # dictionary, it does not need to implement __setstate__()
    #def __setstate__(self, state):
    #    pass

    def __call__(self, exception=True):
        """
        Compute the value of the body of this constraint.

        This method does not simply return self.value because that data value may be out of date
        w.r.t. the value of decision variables.
        """

        if self.body is None:
            return None
        return self.body()

    def lslack(self):
        """
        Returns the value of L-f(x) for constraints of the form:
            L <= f(x) (<= U)
            (U >=) f(x) >= L
        """
        if self.lower is None:
            return float('-inf')
        else:
            return value(self.lower)-value(self.body)

    def uslack(self):
        """
        Returns the value of U-f(x) for constraints of the form:
            (L <=) f(x) <= U
            U >= f(x) (>= L)
        """
        if self.upper is None:
            return float('inf')
        else:
            return value(self.upper)-value(self.body)


class Constraint(ActiveIndexedComponent):
    """
    An object that defines a objective expression

    Construct an objective expression with rule to construct the
    expression

    keyword arguments:
    name: name of this object
    rule: function or rule definition of constraint
    expr: same as rule
    doc:  documentation string for constraint
    """

    NoConstraint    = (1000,)
    Skip            = (1000,)
    Infeasible      = (1001,)
    Violated        = (1001,)
    Feasible        = (1002,)
    Satisfied       = (1002,)

    def __new__(cls, *args, **kwds):
        if cls != Constraint:
            return super(Constraint, cls).__new__(cls)
        if args == ():
            return _ConstraintElement.__new__(_ConstraintElement)
        else:
            return _ConstraintArray.__new__(_ConstraintArray)

    def __init__(self, *args, **kwargs):
        tmprule = kwargs.pop('rule', None )
        tmprule = kwargs.pop('expr', tmprule )
        self.rule = tmprule
        self.trivial = False
        self._no_rule_init = kwargs.pop('noruleinit', None )
        #
        kwargs.setdefault('ctype', Constraint)
        ActiveIndexedComponent.__init__(self, *args, **kwargs)

    def construct(self, data=None):
        """TODO"""
        #
        # cache the debug generation flag, to avoid the expense of
        # calling isEnabledFor() for each index - this is far too
        # expensive an operation to perform deep in a loop. the only
        # potential down-side is that the debug logging is either
        # disabled or enabled globally for the duration of this
        # method invocation - which doesn't seem like much of
        # (if any) limitation in practice.
        #
        generate_debug_messages = (__debug__ is True) and (logger.isEnabledFor(logging.DEBUG) is True)

        if generate_debug_messages is True:
            logger.debug("Constructing constraint %s",self.cname(True))

        if (self._no_rule_init is not None) and (self.rule is not None):
            logger.warn("noruleinit keyword is being used in conjunction with "
                        "rule keyword for constraint '%s'; defaulting to "
                        "rule-based construction.", self.cname(True))
        if self.rule is None:
            if self._no_rule_init is None:
                logger.warn("No construction rule or expression specified for "
                            "constraint '%s'", self.cname(True))
            else:
                self._constructed=True
            return

        if self._constructed:
            return

        self._constructed=True
        
        #
        # Local variables for code optimization
        #
        _self_rule = self.rule
        _self_parent = self._parent()
        #
        # a somewhat gory way to see if you have a singleton - the len()=1 check is 
        # needed to avoid "None" being passed illegally into set membership validation rules.
        #
        if (len(self._index) == 1) and (None in self._index): 
            if len(self._index) != 1:
                raise IndexError("Internal error: constructing constraint "\
                    "with both None and Index set")
            if generate_debug_messages:
                logger.debug("  Constructing single constraint (index=None)")
            if _self_rule.__class__ is bool or isinstance(_self_rule,_ExpressionBase):
                expr = _self_rule
            else:
                expr = _self_rule(_self_parent)
            self.add(None, expr)
        else:
            if _self_rule.__class__ is bool or isinstance(_self_rule,_ExpressionBase):
                raise IndexError("Cannot define multiple indices in a " \
                    "constraint with a single expression")
            for index in self._index:
                if generate_debug_messages:
                    logger.debug("  Constructing constraint index "+str(index))
                try:
                    expr = apply_indexed_rule( 
                        self, _self_rule, _self_parent, index )
                except Exception:
                    err = sys.exc_info()[1]
                    logger.error(
                        "Rule failed when generating expression for "
                        "constraint %s:\n%s: %s" 
                        % ( self.cname(True), type(err).__name__, err ) )
                    raise 
                self.add( index, expr )

    def add(self, index, expr):
        # index: the constraint index (should probably be renamed)
        # expr: the constraint expression

        expr_type = expr.__class__

        # Convert deprecated expression values
        #
        if expr_type in _simple_constraint_rule_types:
            if expr is None:
                raise ValueError("""
Invalid constraint expression.  The constraint expression resolved to
None instead of a Pyomo object.  Please modify your rule to return
Constraint.Skip instead of None.

Error thrown for Constraint "%s"
""" % ( self.cname(True), ) )

            # There are cases where a user thinks they are generating a
            # valid 2-sided inequality, but Python's internal systems
            # for handling chained inequalities is doing something very
            # different and resolving it to True/False.  In this case,
            # chainedInequality will be non-None, but the expression
            # will be a bool.  For example, model.a < 1 > 0.
            if generate_relational_expression.chainedInequality is not None:
                buf = StringIO.StringIO()
                generate_relational_expression.chainedInequality.pprint(buf)
                # We are about to raise an exception, so it's OK to reset chainedInequality
                generate_relational_expression.chainedInequality = None
                raise ValueError("""
Invalid chained (2-sided) inequality detected.  The expression is
resolving to %s instead of a Pyomo Expression object.  This can occur
when the middle term of a chained inequality is a constant or immutable
parameter, for example, "model.a <= 1 >= 0".  The proper form for
2-sided inequalities is "0 <= model.a <= 1".

Error thrown for Constraint "%s"

Unresolved (dangling) inequality expression:
    %s
""" % ( expr, self.cname(True), buf ) )
            else:
                raise ValueError("""
Invalid constraint expression.  The constraint expression resolved to a
trivial Boolean (%s) instead of a Pyomo object.  Please modify your rule
to return Constraint.%s instead of %s.

Error thrown for Constraint "%s"
""" % ( expr, expr and "Feasible" or "Infeasible", expr, self.cname(True) ) )

        #
        # Ignore an 'empty' constraint
        #
        if expr_type is tuple and len(expr) == 1:
            if expr == Constraint.Skip or expr == Constraint.Feasible:
                return
            if expr == Constraint.Infeasible:
                raise ValueError( "Constraint '%s' is always infeasible" % 
                                  self.cname(True) )
        #
        #
        # Local variables to optimize runtime performance
        #
        if index is None:
            conData = self
        else:
            conData = _ConstraintData(self)
        #
        if expr_type is tuple: # or expr_type is list:
            #
            # Form equality expression
            #
            if len(expr) == 2:
                arg0 = expr[0]
                if arg0 is not None:
                    arg0 = as_numeric(arg0)
                arg1 = expr[1]
                if arg1 is not None:
                    arg1 = as_numeric(arg1)

                conData._equality = True
                if arg1 is None or arg1.is_fixed():
                    conData.lower = conData.upper = arg1
                    conData.body = arg0
                elif arg0 is None or arg0.is_fixed():
                    conData.lower = conData.upper = arg0
                    conData.body = arg1
                else:
                    conData.lower = conData.upper = ZeroConstant
                    conData.body = arg0 - arg1
            #
            # Form inequality expression
            #
            elif len(expr) == 3:
                arg0 = expr[0]
                if arg0 is not None:
                    arg0 = as_numeric(arg0)
                    if not arg0.is_fixed():
                        raise ValueError(
                            "Constraint '%s' found a 3-tuple (lower, " 
                            "expression, upper) but the lower value was "
                            "non-constant." % self.cname(True) )

                arg1 = expr[1]
                if arg1 is not None:
                    arg1 = as_numeric(arg1)

                arg2 = expr[2]
                if arg2 is not None:
                    arg2 = as_numeric(arg2)
                    if not arg2.is_fixed():
                        raise ValueError(
                            "Constraint '%s' found a 3-tuple (lower, " 
                            "expression, upper) but the upper value was "
                            "non-constant" % self.cname(True) )

                conData.lower = arg0
                conData.body  = arg1
                conData.upper = arg2
            else:
                raise ValueError(
                    "Constructor rule for constraint '%s' returned a tuple" 
                    ' of length %d.  Expecting a tuple of length 2 or 3:\n' 
                    'Equality:   (left, right)\n' 
                    'Inequality: (lower, expression, upper)'
                    % ( self.cname(True), len(expr) ))

            relational_expr = False
        else:
            try:
                relational_expr = expr.is_relational()
                if not relational_expr:
                    raise ValueError(
                        "Constraint '%s' does not have a proper value.  " 
                        "Found '%s'\nExpecting a tuple or equation.  "
                        "Examples:\n" 
                        "    summation( model.costs ) == model.income\n" 
                        "    (0, model.price[ item ], 50)"
                        % ( self.cname(True), str(expr) ))
            except AttributeError:
                msg = "Constraint '%s' does not have a proper value.  " \
                      "Found '%s'\nExpecting a tuple or equation.  " \
                      "Examples:\n" \
                      "    summation( model.costs ) == model.income\n" \
                      "    (0, model.price[ item ], 50)" \
                      % ( self.cname(True), str(expr) )
                if type(expr) is bool:
                    msg +="""
Note: constant Boolean expressions are not valid constraint expressions.
Some apparently non-constant compound inequalities (e.g. "expr >= 0 <= 1")
can return boolean values; the proper form for compound inequalities is
always "lb <= expr <= ub"."""
                raise ValueError(msg)
        #
        # Special check for chainedInequality errors like "if var < 1:"
        # within rules.  Catching them here allows us to provide the
        # user with better (and more immediate) debugging information.
        # We don't want to check earlier because we want to provide a
        # specific debugging message if the construction rule returned
        # True/False; for example, if the user did ( var < 1 > 0 )
        # (which also results in a non-None chainedInequality value)
        #
        if generate_relational_expression.chainedInequality is not None:
            from expr import chainedInequalityErrorMessage
            raise TypeError(chainedInequalityErrorMessage())
        #
        # Process relational expressions (i.e. explicit '==', '<', and '<=')
        #
        if relational_expr:
            if expr_type is _EqualityExpression:
                # Equality expression: only 2 arguments!
                conData._equality = True
                if expr._args[1].is_fixed():
                    conData.lower = conData.upper = expr._args[1]
                    conData.body = expr._args[0]
                elif expr._args[0].is_fixed():
                    conData.lower = conData.upper = expr._args[0]
                    conData.body = expr._args[1]
                else:
                    conData.lower = conData.upper = ZeroConstant
                    conData.body = generate_expression_bypassCloneCheck(_sub, expr._args[0], expr._args[1])
            else:
                # Inequality expression: 2 or 3 arguments
                if True in expr._strict:
                    #
                    # We can relax this when:
                    #   (a) we have a need for this
                    #   (b) we have problem writer that explicitly
                    #       handles this
                    #   (c) we make sure that all problem writers
                    #       that don't handle this make it known to
                    #       the user through an error or warning
                    #
                    raise ValueError(
                        "Constraint '%s' encountered a strict inequality "
                        "expression ('>' or '<'). All constraints must be "
                        "formulated using using '<=', '>=', or '=='." 
                        % (self.cname(True),) )
                if len(expr._args) == 3:
                    if not expr._args[0].is_fixed():
                        msg = "Constraint '%s' found a double-sided "\
                              "inequality expression (lower <= expression "\
                              "<= upper) but the lower bound was non-constant"
                        raise ValueError(msg % (self.cname(True),))
                    if not expr._args[2].is_fixed():
                        msg = "Constraint '%s' found a double-sided "\
                              "inequality expression (lower <= expression "\
                              "<= upper) but the upper bound was non-constant"
                        raise ValueError(msg % (self.cname(True),))
                    conData.lower = expr._args[0]
                    conData.body  = expr._args[1]
                    conData.upper = expr._args[2]
                else:
                    if expr._args[1].is_fixed():
                        conData.lower = None
                        conData.body  = expr._args[0]
                        conData.upper = expr._args[1]
                    elif expr._args[0].is_fixed():
                        conData.lower = expr._args[0]
                        conData.body  = expr._args[1]
                        conData.upper = None
                    else:
                        conData.lower = None
                        conData.body  = generate_expression_bypassCloneCheck(_sub, expr._args[0], expr._args[1])
                        conData.upper = ZeroConstant
        #
        # Replace numeric bound values with a NumericConstant object,
        # and reset the values to 'None' if they are 'infinite'
        #
        if conData.lower is not None:
            val = conData.lower()
            if not pyutilib.math.is_finite(val):
                if val > 0:
                    msg = "Constraint '%s' created with a +Inf lower bound"
                    raise ValueError(msg % ( self.cname(True), ))
                conData.lower = None
            elif bool(val > 0) == bool(val <= 0):
                msg = "Constraint '%s' created with a non-numeric lower bound"
                raise ValueError(msg % ( self.cname(True), ))
        if conData.upper is not None:
            val = conData.upper()
            if not pyutilib.math.is_finite(val):
                if val < 0:
                    msg = "Constraint '%s' created with a -Inf upper bound"
                    raise ValueError(msg % ( self.cname(True), ))
                conData.upper = None
            elif bool(val > 0) == bool(val <= 0):
                msg = "Constraint '%s' created with a non-numeric upper bound"
                raise ValueError(msg % ( self.cname(True), ))
        #
        # Error check, to ensure that we don't have a constraint that
        # doesn't depend on any variables / parameters
        #
        # Error check, to ensure that we don't have an equality constraint with
        # 'infinite' RHS
        #
        if conData._equality:
            if conData.lower != conData.upper: #pragma:nocover
                msg = "Equality constraint '%s' has non-equal lower and "\
                      "upper bounds (this is indicitive of a SERIOUS "\
                      "internal error in Pyomo)."
                raise RuntimeError(msg % self.cname(True))
            if conData.lower is None:
                msg = "Equality constraint '%s' defined with non-finite term"
                raise ValueError(msg % self.cname(True))
        #
        # hook up the constraint data object to the parent constraint.
        #
        self._data[index] = conData

    def _pprint(self):
        return ( 
            [("Size", len(self)),
             ("Index", self._index \
                  if self._index != UnindexedComponent_set else None),
             ("Active", self.active),
             ],
            iteritems(self._data),
            ( "Key","Lower","Body","Upper","Active" ),
            lambda k, v: [ k,
                           "-Inf" if v.lower is None else v.lower,
                           v.body,
                           "+Inf" if v.upper is None else v.upper,
                           v.active,
                           ]
            )


    def Xpprint(self, ostream=None, verbose=False, prefix="   "):
        """TODO"""
        tab = "    "
        if ostream is None:
            ostream = sys.stdout
        ostream.write(prefix+self.cname()+" : ")
        if self.doc is not None:
            ostream.write(self.doc+'\n'+prefix+tab)
        ostream.write("Size="+str(len(self)))
        if isinstance(self._index,Set):
            ostream.write(" Index="+self._index.cname(True))
        ostream.write(" Active="+str(self.active))
        if not self._constructed:
            ostream.write("\n"+prefix+tab+"Not constructed\n")
            return
        
        ostream.write("\n")
        prefix = prefix+tab
        for key in sorted(self._data):
            if self.is_indexed():
                ostream.write(prefix+str(key)+
                              ' (Active='+str(self._data[key].active)+')\n')
            if self._data[key].lower is not None:
                ostream.write(prefix+tab)
                if self._data[key].lower.is_expression():
                    self._data[key].lower.pprint(ostream)
                else:
                    ostream.write(str(self._data[key].lower))
                ostream.write('\n')
            else:
                ostream.write(prefix+tab+"-Inf\n")
            ostream.write(prefix+tab+"<=\n")
            if self._data[key].body is not None:
                ostream.write(prefix+tab)
                if self._data[key].body.is_expression():
                    self._data[key].body.pprint(ostream)
                else:
                    ostream.write(str(self._data[key].body))
                ostream.write('\n')
            ostream.write(prefix+tab+"<=\n")
            if self._data[key].upper is not None:
                ostream.write(prefix+tab)
                if self._data[key].upper.is_expression():
                    self._data[key].upper.pprint(ostream)
                else:
                    ostream.write(str(self._data[key].upper))
                ostream.write('\n')
            elif self._data[key]._equality:
                ostream.write(prefix+tab)
                if self._data[key].lower.is_expression():
                    self._data[key].lower.pprint(ostream)
                else:
                    ostream.write(str(self._data[key].lower))
                ostream.write('\n')
            else:
                ostream.write(prefix+tab+"Inf\n")

    def display(self, prefix="", ostream=None):
        """TODO"""
        if not self.active:
            return
        if ostream is None:
            ostream = sys.stdout
        tab="    "
        ostream.write(prefix+self.cname()+" : ")
        ostream.write("Size="+str(len(self)))

        ostream.write("\n")
        tabular_writer( ostream, prefix+tab, 
                        ((k,v) for k,v in iteritems(self._data) if v.active),
                        ( "Key","Lower","Body","Upper" ),
                        lambda k, v: [ k,
                                       value(v.lower),
                                       v.body(),
                                       value(v.upper),
                                       ] )



class _ConstraintElement(Constraint, _ConstraintData):

    def __init__(self, *args, **kwd):
        _ConstraintData.__init__(self, self)
        Constraint.__init__(self, *args, **kwd)

    def __call__(self, exception=True):
        """Compute the value of the constraint body"""

        if not self._constructed is True:
            raise ValueError("Constraint %s has not been construced" % self.cname(True))

        if self.body is None:
            return None
        return value(self.body)

    # all model components need to possess a "reset" method. because neither Constraint and
    # _ConstraintData are derived from NumericValue, the method is needed here. ultimately,
    # the right answer is to either nix the reset() from everywhere (it is not particularly
    # well-defined at the moment), or add it to the common Constraint base class.
    def reset(self):
        pass

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


class _ConstraintArray(Constraint):

    def __call__(self, exception=True):
        """Compute the value of the constraint body"""
        if exception:
            msg = 'Cannot compute the value of an array of constraints'
            raise ValueError(msg)


class ConstraintList(_ConstraintArray):
    """
    A constraint component that represents a list of constraints.
    Constraints can be indexed by their index, but when they are added
    an index value is not specified.
    """

    End             = (1003,)

    def __init__(self, **kwargs):
        """Constructor"""
        #if args:
        #    raise ValueError("Cannot specify indices for a "
        #                     "ConstraintList object")
        #
        args = (Set(),)
        self._nconstraints = 0
        Constraint.__init__(self, *args, **kwargs)

    def construct(self, data=None):
        """TODO"""
        #
        if self._constructed:
            return
        self._index.construct()
        self._constructed=True

        if self.rule is None:
            return

        generate_debug_messages = (__debug__ is True) and \
                                  (logger.isEnabledFor(logging.DEBUG) is True)

        if generate_debug_messages is True:
            logger.debug("Constructing constraint list %s",self.cname(True))

        if (self._no_rule_init is not None) and (self.rule is not None):
            msg = 'WARNING: noruleinit keyword is being used in conjunction ' \
                  "with rule keyword for constraint '%s'; defaulting to "     \
                  'rule-based construction.'
            print(msg % self.cname(True))
        #
        # Local variables for code optimization
        #
        while True:
            val = self._nconstraints + 1
            if generate_debug_messages is True:
                logger.debug("   Constructing constraint index "+str(val))
            expr = apply_indexed_rule( self, self.rule, self._parent(), val )
            if not isgenerator(expr):
                expr = (expr,)
            for e in expr:
                if e is None:
                    #logger.warning(
                    #    "DEPRECATION WARNING: Constraint rule returned None "
                    #    "instead of ConstraintList.End" )
                    raise ValueError( "Constraint rule returned None "
                                      "instead of ConstraintList.End" )
                if (e.__class__ is tuple and e == ConstraintList.End):
                    #or (type(e) in (int, long, float) and e == 0):
                    return
                self.add(e)

    def add(self, expr):
        """TODO"""
        self._nconstraints += 1
        Constraint.add(self, self._nconstraints, expr)


register_component(Constraint, "Constraint expressions in a model.")
register_component(ConstraintList, "A list of constraints in a model.")


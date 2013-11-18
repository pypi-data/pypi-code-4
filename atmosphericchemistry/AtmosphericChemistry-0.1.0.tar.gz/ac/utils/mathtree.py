# -*- coding: utf-8 -*-
"""
mathTree

Python class to parse and evaluate mathematical equations and perform a minimal set of
algebraic operations (mainly factorisation). The term (a string argument upon initialisation)
will be converted into a tree structure on which all numerical and algebraic operations are
performed. str() will convert the tree back into a nicely formatted term string.

Allowed operators for mathTree are:
Binary operators:  +, -, *, /, % (modulo), ^ (or **)
Unary operators (functions): exp, log, ln, sqrt, sin, cos, tan, sinh, cosh, tanh, abs,
      round, trunc, ceil, sign (or sgn), d2r (degree to radians), r2d (radians to degrees).
      It is easy to add operators by modifying the _set_operators method.

The mathTree class also defines a couple of numerical values, namely 'e' (Euler's number)
and 'pi'.

A typical use example might be:
      t = mathTree("x*(x+y)/(3*sin(x))")    # build tree from string
      t.set_variable(x=7., y=-2.2)          # define variable values
      print "The expression %s with x=%f and y=%f yields %f."%  \
            (str(t),t.variables["x"],t.variables["y"],t.evaluate())
      t.factorize()                         # algebra
      t.print_term()                        # equivalent to print str(t)

Note: This object class has primarily been written for the purposes of
1) parsing and factorizing the product side of reaction equations such as
      '.7 * (CH2O + CH3CHO + HO2) + .3 * (CH3OH + C2H5OH)' and 
2) evaluating expressions for reaction rate coefficients (e.g. '2.4e-12*exp(-1230./T)').
It might be suited for other applications, but do so at your own risk. Algebraic transformations
are limited, and you may be better of trying the sympy package. For example, mathTree
doesn't recognize that x*x is the same as x^2 (although it will evaluate both forms correctly).
Parsing is not optimized (I only discovered after writing 80% of this that there are better
algorithms readily available), and for more complex math one should reqrite this to use
proper grammar package (e.g. pyparsing).

The module contains two test suites: testsuite_evaluate for testing of parsing and numerical
correctness, and testsuite_factorisation for testing of algebra.


Class documentation:

Instantiation:
- c = mathTree(term)  , where term is a string containing a mathematical expression
Attributes:
- _root: the root node of the tree (a mathNode instance)
- _variables: dictionary with variable names and values (can be accessed as t.variables)
- _defaults: dictionary with variable default values
- _operator: dictionary with binary operators and the functions to evaluate them numerically
- _oprank: a dictionary with operator ranking numbers (so far used only for reconstructung
      a string from the tree. Could also be used for parsing a term (see for example
      http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm).
- _uoperator: dictionary with unary function names and the functions to evaluate them numerically
- _resolved: a bool flag to indicate if the term has been searched for variables and numerical
      values (set True in find_variables method)
Interface Methods:
- t.cleanup([node]): perform a couple of cleanup operations such as removing nodes where zero
      is added, multiplication by zero, etc. Also evaluates expressions that are purely
      numerical (i.e. no variables involved). Normally, cleanup is called automatically
      after algebraic operations.
- t.combine_terms([node]): combine terms of the form [factor*]subnode into sum(factors)*subnode.
      This method is called from factorize() to clean up afterwards. Note that combine_terms
      may lead to the removal of variables which then become undefined.
- t.copy(): returns a clone (deep copy) of itself.
- t.evaluate([node]): evaluate the term numerically. If the term contains variables, these must
      first be set using the set_variable method. Note that pi (3.14...) and e (2.71...)
      are pre-defined. It is planned to add fucntionality in the future to load other
      variable dictionaries, e.g. from air.py.
      Evaluate returns a numerical value if successful, or None if any variable is undefined.
- t.factorize([node]): factorize the tree (i.e. remove parantheses as much as possible).
      Afterwards the factorized terms will be combined where possible. Note, however, that
      mathTree doesn't recognize that x^2 is the same as x*x.
- t.get_default(variable): return the default value for a given variable name. Currently,
      the only variable names with default values are 'e' and 'pi'.
      [not quite correct but users shouldn't take the others for granted]
- t.isnode(arg): returns true if the argument is a mathNode.
- t.isnumber(arg): returns true if the argument is a float value.
- t.isvalue(arg): returns true if the argument is a numeric value (number) or a variable.
- t.isvariable(arg): returns true if the argument is a variable name (actually just a string).
- t.print_term([node]): print a string expression of the tree (or any node within). This is
      a convenience method equivalent to 'print str(t)'.
- t.rank(node): returns an integer value depending on whether the argument is a numeric (float)
      value (= 0), a variable name (= 1), or a node (mathNode object, = 2).
- t.resolve([node]): identify variables and numerical values in the tree after parsing. This is
      normally done automatically as soon as you invoke numerical evaluation or algebra,
      but there may be occasions when you wish to resolve a tree manually before setting
      variables etc., for example to define additional default values or test if certain
      variables are contained in the term, etc.
- t.set_variable(**kwargs): set variable values. These can be provided as a dictionary (with
      prepended '**' signs, or via keyword arguments. The method will raise an error if
      you attempt to set a variable which is not defined in the term. This behaviour can
      be switched off with the ignore_error keyword.
- t.simplify([node]): performs a couple of algebraic operations to simplify the tree structure
      and allow for combining terms, evaluating numerical portions of the term, etc. This
      is only somewhat systematic, but appears to work in general.
- t.termsplit(subterm, op) [parsing]: split mathematical term into left and right around
      the operator op, thereby respecting groups enclosed in parantheses.
- t.variables: a property method to access variable values. Behaves like a dictionary. Thus,
      t.variables["x"] will return the value of the variable x is this is defined.

      
Local methods (generally not to be invoked by the user):
a) initialisation:
- _count_minus(subterm) [parsing]: handle terms with leading minus signs (e.g. '---9' will
      be reduced to '-9').
- _find_unary_function(subterm) [parsing]: identify a unary function
- _has_parantheses(subterm) [parsing]: check if the subterm is enclosed in parantheses
- _identify_subtractions(term) [parsing]: replace all subtraction '-' signs with '~' to distinguish
      them from minus signs
- _parse_term(term): dissect the string with the mathematical term and build the tree
- _set_defaults(): set default values for frequently used variables
- _set_operators(): defines the binary and unary operators upon initialisation
      
b) numerical evaluation:
- _check_undefined_variables(): reports any variables that were found in the expression but
      have not been assigned a numerical value. This method will raise an error if undefined
      variables are found. 
- _evaluate(node): the actual work function for numerical evaluation of the term

c) printing of terms:
- _tostring([node]): converts the tree to a string representation (which could again be parsed
      by mathTree).
      
d) cleanup functions:
- _remove_atoms(node): removes 'empty' nodes of the form (value, None, None)
- _remove_mult_zero(node): removes nodes where a value is multiplied with zero
- _remove_div_zero(node): removes nodes where zero is divided by something
- _remove_mod_zero(node): removes nodes with 0 modulo something
- _remove_mult_one(node): removes factors of 1.0
- _remove_divby_one(node): removes division by 1.0
- _remove_add_zero(node): removes addition of 0
- _remove_sub_zero(node): remove subtraction of 0
- _remove_subfrom_zero(node): converts 0-x to (-1)*x
- _remove_num_ops(node): evaluates purely numerical expressions and replaces them with the result
- _rearrange_left_right(node): arrange node elements so that factors tend to be left of variables and
      variables left of nodes. 
- _sort_variables(node): sort variables in a node alphabetically if permitted

e) simplify functions:
- _lrr_to_llr(node): transform pattern 'a op (b op x)' to '(a op b) op x'
- _lrr_to_llr2(node): transform pattern 'a op (x op b)' to '(a op b) op x'
- _llr_to_llr(node): transform pattern '(a op x) op b' to '(a op b) op x'
- _llr_to_lrr(node): transform pattern '(x op a) op b' to 'x op (a op b)'
- _move_node_to_left(node): transform 'x op (y op z)' to '(x op y) op z'
- _extract_factor(node): extract numerical factors in '(a * x) op y' to become
      'a * (x op y)' [op = '*' or '/']
- _remove_double_negative(node): convert '- (negative * x)' to '+ (positive * x)'
      and '+ (negative * x)' to '- (positive * x)'

f) algebra functions:
- add_term_factors(node): add '1. *' in front of terms that could be combined
- add_terms(n1, n2): add the second node to the first one assuming this is mathematically
      correct. If the left branch of n1 or n2 is a numerical factor this will be used,
      otherwise the factor is assumed to be 1. The second node will become an atom with
      the value of 0 afterwards. The cleanup() method is called to get rid of this
      afterwards. The add_terms method is called from combine_terms().
- _build_nodelist_t(node): build a list of nodes below node that are connected by
      '+' or '~' operators, which themeselves don't have addition or subtraction nodes
      as children. This is needed for combine_terms().
- _combine_terms(node): attempt to combine equal terms and add up their factors


mathTree also makes use of a mathNode object class, which is fairly simple and
straightforward. It defines three attributes: left, op,and right which can be
read and written directly (e.g. node.left.left=something). Empty nodes have three
None values, (scalar) constants are float instances, variables are basestring
instances, and everything else is assumed to be another mathNode. If op is None,
only the left field may be occupied and denotes a scalar value (temporary state),
if left is None, op must be a unary function name ("exp", "sin", etc.). If op is
not None, right must not be None either. MathNode provides two user methods:
isatom() [tests for op is None] and swap_branches() [exchanges left and right attributes].
"""

from collections import OrderedDict
from copy import deepcopy
import numpy as np
import re
from ac.utils import format_number


__author__ = 'Martin Schultz'
__email__ = 'm.schultz@fz-juelich.de'
__version__ = '1.0'
__date__ = '2013-09-26'
__license__ = 'MIT'


# regular expression pattern (to remove "+" in "1.23e+3")
p_eplus = re.compile(r"([.0-9][eE])\+([0-9])")


class mathNode(object):
    """defines a simple two operand relationship for recursive use in mathTree."""

    def __init__(self, value=None):
        """construct a new node
        Input argument is normally a tuple (left, op, right)
        If value is None, a tuple (None, None, None) will be assumed
        If value is a single string, it equates to (value, None, None)"""
        if value is None:
            (self._left, self._op, self._right) = (None, None, None)
        elif isinstance(value, basestring):
            (self._left, self._op, self._right) = (value, None, None)
        else:
            (self._left, self._op, self._right) = value


    @property
    def left(self):
        return self._left
    

    @left.setter
    def left(self, value):
        self._left = value

        
    @property
    def right(self):
        return self._right
    

    @right.setter
    def right(self, value):
        self._right = value

        
    @property
    def op(self):
        return self._op


    @op.setter
    def op(self, value):
        self._op = value


    def __str__(self):
        if isinstance(self.left, mathNode):
            l = "(%s)" % (str(self.left))
        else:
            l = str(self.left)
        op = " %s " % (self.op) if not self.op is None else ""
        if self.right is None:
            r = ""
        elif isinstance(self.right, mathNode):
            r = "(%s)" % (str(self.right))
        else:
            r = str(self.right)
        return l + op + r

    
    def isatom(self):
        return self._op is None
    

    def swap_branches(self):
        if not (self.left is None or self.right is None):
            tmp = self._left
            self._left = self._right
            self._right = tmp



                 
class mathTree(object):
    """builds a tree structure from a (simple) mathematical expression and contains
    a few functions to simplify and evaluate expressions with '+', '*', '()', numbers
    and variables.
    Note: a much more comprehensive python package to do this (and more) is under
    development as sympy."""

    # --- initialisation and attributes ---
    def __init__(self, term, autoexecnumops=True):
        """build a new tree from a string.
        Autormnumops controls automatic execution of operators involving
        only numbers."""
        self._set_operators()
        self._root = self._parse_term(term)
        self._variables = {}
        self._set_defaults()   # set default values for frequently used variables
        self._resolved = False # set to True in resolve method
        self._autoexecnumops = autoexecnumops
        

    @property
    def variables(self):
        return self._variables


    def __str__(self):
        """String representation of object."""
        return self._tostring()

    
    def _set_defaults(self):
        """Define a couple of reasonable default values for frequently used variables"""
        d = {}
        d["e"] = np.e
        d["pi"] = np.pi
        # the following should be moved to air.py once that exists properly
        d["T"] = 298.     # temperature in K
        d["p"] = 101325.  # pressure in Pa
        d["M"] = 2.77e19  # air density STP in molec cm-3
        d["Avo"] = 6.02214129e23  # Avogadro constant
        d["kB"] = 1.3806488e-23   # Boltzmann constant (J/K)
        d["R"] = 8.31432  # J mol-1 K-1
        d["Ra"] = 286.9   # individual gas constant air (J/kg K)
        d["Rw"] = 461.5   # individual gas constant water (J/kg K)
        d["g"] = 9.80665  # acceleration due to gravity (m/s)
        self._defaults = d

        
    def _set_operators(self):
        """Define operators and their functions (upon initialisation)"""
        # binary operators
        d = OrderedDict()
        d["+"] = lambda x, y: x + y
        d["~"] = lambda x, y: x - y   # note ~ for -
        d["*"] = lambda x, y: x * y
        d["/"] = lambda x, y: x / y
        d["%"] = lambda x, y: x % y
        d["^"] = lambda x, y: x**y
        self._operator = d
        # unary operators
        d = OrderedDict()
        d["exp"] = lambda x: np.exp(x)
        d["log"] = lambda x: np.log10(x)
        d["ln"]  = lambda x: np.log(x)
        d["sqrt"] = lambda x: np.sqrt(x)
        d["sin"] = lambda x: np.sin(x)
        d["cos"] = lambda x: np.cos(x)
        d["tan"] = lambda x: np.tan(x)
        d["sinh"] = lambda x: np.sinh(x)
        d["cosh"] = lambda x: np.cosh(x)
        d["tanh"] = lambda x: np.tanh(x)
        d["abs"] = lambda x: np.abs(x)
        d["round"] = lambda x: np.round(x)
        d["trunc"] = lambda x: np.trunc(x)
        d["ceil"] = lambda x: np.ceil(x)
        d["sign"] = lambda x: np.sign(x)
        d["sgn"] = lambda x: np.sign(x)
        d["d2r"] = lambda x: x * np.pi / 180.
        d["r2d"] = lambda x: x * 180. / np.pi
        self._uoperator = d
        # define operator ranking
        # + and ~, and * and / have same ranking
        r = OrderedDict()
        j = 0
        for k in self._operator:
            r[k] = j
            if not (k == '+' or k == '*'):
                j += 1
        # make room for '^' as highest rank
        r["^"] = 99
        # add functions all with rank 50
        for k in self._uoperator:
            r[k] = 50
        # add None and empty
        r[""] = 999
        r[None] = 999
        self._oprank = r
        


    # --- management ---
    def copy(self):
        """Returns a copy of itself"""
        return deepcopy(self)

    
    # --- parsing ---
    def _count_minus(self, s):
        """return the leading number of '-' signs in s."""
        res = 0
        for i in range(len(s)):
            if s[i] == '-':
                res += 1
            else:
                break
        return res

    
    def _find_unary_function(self, s):
        """Identify common mathematical functions such as exp, sin, cos"""
        lterm = s.lower()
        for n in self._uoperator.keys():
            if lterm.startswith(n+"("):
                return n
        return None
    
                
    def _has_parantheses(self, s):
        return s.startswith("(") and s.endswith(")")
    

    def _identify_subtractions(self, term):
        """Find - signs that are subtraction and not -number or e-"""
        term = list(term)
        for i, c in enumerate(term):
            if c == "-":
                # look for exponential
                if i > 2 and term[i-1] in "eEdD" and term[i-2] in ".0123456789":
                    continue
                # look for -number
                if i == 0 or term[i-1] in "(-+*/^":
                    continue
                # we're here so it must be a subtraction
                term[i] = "~"
        return "".join(term) 


    def _parse_term(self, term, level=0, branch=""):
        """Recursively parse a mathematical term thereby looping through operators according
        to precedence.
        Notes:
        1) this is not a very efficient algorithm as it re-reads the string several times
        For professional parsing algorithms with tree building, see for example
        http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
        2) the string is always analyzed right to left, except for '^'
        3) subtraction is replaced with '~' to distinguish from negative values
        4) mathematical operators and functions are only defined to the extent needed
        in this atmospheric chemistry application
        5) the level keyword is used internally - the branch keyword is for debugging only"""
#        print "###%i:%s  [%s]"%(level,term,branch)
        oplast = self._operator.keys()[-1]
        # remove blanks, replace subtraction sign with "~" and double ** with ^
        if level == 0:
            term = self._identify_subtractions(term)
            term = term.replace(" ", "")
            term = term.replace("\t", "")
            term = term.replace("**", "^")
            term = re.sub(p_eplus, r"\1\2", term)
        node = mathNode( (None, None, None) )
        for op in self._operator.keys():
            direction = 1 if op == "^" else -1
            left, right = self.termsplit(term, op, direction=direction)
            if right is None:
                if op == oplast:
                    # found an 'elemental' left node. May still be a unary function
                    # or an expression in parantheses
                    f = self._find_unary_function(left)
                    if f:
                        subnode = self._parse_term(left[len(f)+1:-1], level+1, branch="(func)")
                        node.left = mathNode( (None, left[0:len(f)], subnode) )
                        break
                    elif self._has_parantheses(left):
                        node.left = self._parse_term(left[1:-1], level+1, branch="(left)")
                        break
                    else:
                        # atomic expression
                        # first, we must count leading '-' though
                        nminus = self._count_minus(left)
                        if nminus > 1:
                            left = left[(nminus//2)*2:]
                        node.left = left
            elif left is None:
                if op == oplast:
                    # found an 'elemental' right node. May still be a unary function
                    # or an expression in parantheses
                    f = self._find_unary_function(right)
                    if f:
                        subnode = self._parse_term(right[len(f)+1:-1], level+1, branch="(func)")
                        node.right = mathNode( (None, left[0:len(f)], subnode) )
                        break
                    elif self._has_parantheses(right):
                        node.right = self._parse_term(right[1:-1], level+1, branch="(right)")
                        break
                    else:
                        # atomic expression
                        # first, we must count leading '-' though
                        nminus = self._count_minus(right)
                        if nminus > 1:
                            right = right[(nminus//2)*2:]
                        node.right = right
            else:
                # operator was found -> recursively analyze left and right side
                node.op = op
                node.left = self._parse_term(left, level+1, branch="left")
                node.right = self._parse_term(right, level+1, branch="right")
                break
        if level > 0 and node.isatom():
            node = node.left
        return node


    def _tostring(self, node=None):
        """Formats a node in normal notation. The user should call str(node) instead
        or print directly with t.print_term(node)."""
        left = ""
        right = ""
        if node is None:
            node = self._root
        if not self.isnode(node):
            print "### not a node %s - shouldn't happen!" % (str(node))
            # return variable or numeric value
            if self.isvariable(node):
                return node  # already string
            elif self.isnumber(node):
                return format_number(node)
            else:
                return ""  # None
        # check left and right sides and test if parantheses must be added
        if self.isnode(node.left):
            left = self._tostring(node.left)
            if self._oprank[node.left.op] < self._oprank[node.op]:
                left = "(%s)" % (left)
        # return variable or numeric value
        elif self.isvariable(node.left):
            left = node.left  # already string
        elif self.isnumber(node.left):
            left = format_number(node.left)
        else:
            left = ""  # None

        if self.isnode(node.right):
            right = self._tostring(node.right)
            if self._oprank[node.right.op] < self._oprank[node.op] or \
               (self._oprank[node.right.op] == self._oprank[node.op] and node.op in "~/"):
                right = "(%s)" % (right)
        # return variable or numeric value
        elif self.isvariable(node.right):
            right = node.right  # already string
        elif self.isnumber(node.right):
            right = format_number(node.right)
        else:
            right = ""  # None

        op = node.op if not node.op is None else ""
        # add parantheses to negative number on left side
        if self.isnumber(node.left) and node.left < 0. and self._oprank[op] < 50:
            left = "(%s)" % (left)
        # add parantheses to function arguments
        if self._oprank[op] == 50:
            right = "(%s)" % (right)
        # replace minus operator with minus sign
        if op == "~":
            op = "-"
        return left+op+right

        
    def print_term(self, node=None):
        """Print the given node (root node if None) in normal notation."""
        print self._tostring(node)
        
        
    def resolve(self, node=None, level=0):
        """Identify variable names and add them to the _variables dictionary.
        As a side-effect, all numbers will be converted to float and negative
        variables will be replaced with a node (-1.0, "*", variable) ."""
        if node is None:
            node = self._root
        # check left side
        if self.isnode(node.left):
            self.resolve(node.left, level+1)
        elif node.left is None:
            pass
        else:
            # see if this is a number or a variable
            try:
                value = float(node.left)
                node.left = value
            except ValueError:
                # this is a variable
                # check for minus
                if node.left.startswith("-"):
                    varname = node.left[1:]
                    node.left = mathNode((-1.0, "*", varname))
                else:
                    varname = node.left
                # make sure varname is valid (must start with letter)
                if varname and not varname[0].isalpha():
                    raise ValueError("Invalid variable name: %s!"%(varname))
                self.variables[varname] = self.get_default(varname)
        # check right side
        if self.isnode(node.right):
            self.resolve(node.right, level+1)
        elif node.right is None:
            pass
        else:
            try:
                value = float(node.right)
                node.right = value
            except ValueError:
                # this is a variable
                if node.right.startswith("-"):
                    varname = node.right[1:]
                    node.right = mathNode((-1.0, "*", varname))
                else:
                    varname = node.right
                self.variables[varname] = self.get_default(varname)
        if level == 0:
            # store numerical constants for cleanup
            self._tiny = np.finfo(float).tiny
            self._eps = np.finfo(float).eps
            # perform cleanup
            self.cleanup()
            # flag resolved status
            self._resolved = True


    def termsplit(self, s, sep, direction=-1):
        """splits a term into left, op, right, leaving sub-terms in parantheses intact"""
        left = None
        right = None
        pc = 0  # parantheses counter
        if direction == 1:
            i0 = 0
            i1 = len(s)
        else:
            i0 = len(s) - 1
            i1 = -1
        for i in range(i0, i1, direction):
            c = s[i]
            if c == sep and pc == 0:
                (left, right) = (s[0:i], s[i+1:])
                return (left, right)
            elif c == "(":
                pc += direction
            elif c == ")":
                pc -= direction
        # error checking
        if pc != 0:
            raise ValueError("Unmatched parantheses in %s" % (s))
        # if we get here, we have an elemental term right or left (or a parantheses expression)
        if direction == 1:
            left = s
        else:
            right = s
        return (left, right)


    # --- type checks for nodes or leafs ---
    def isnode(self, x):
        return isinstance(x, mathNode)


    def isnumber(self, x):
        return isinstance(x, float)


    def isvalue(self, x):
        return self.isnumber(x) or self.isvariable(x)


    def isvariable(self, x):
        return isinstance(x, basestring)


    def rank(self, x):
        """Return 0 for number, 1 for variable and 2 for node"""
        res = None
        if self.isnumber(x):
            res = 0
        elif self.isvariable(x):
            res = 1
        elif self.isnode(x):
            res = 2
        return res

        
    # --- numerical evaluation ---
    def _check_undefined_variables(self):
        """Test if any variables are undefined."""
        undef = []
        for k, v in self._variables.items():
            if v is None:
                undef.append(k)
        if undef:
            msg = ", ".join(sorted([v for v in undef]))
            sp = " is" if len(undef) == 1 else "s are"
            raise ValueError("The following variable%s undefined : %s" % (sp, msg))

    
    def _evaluate(self, node=None):
        """Evaluate the mathematical expression numerically.
        This is the internal function that does the work - the interface is provided by evaluate"""
        val = None
        if node is None:
            node = self._root
        x = y = None
        if self.isnode(node):
#            print "EVALUATE node ",node
            # left branch
            if self.isnode(node.left):
                x = self.evaluate(node.left)
            elif self.isnumber(node.left):
                x = node.left
            elif self.isvariable(node.left):
                x = self.variables[node.left]
            # right branch
            if self.isnode(node.right):
                y = self.evaluate(node.right)
            elif self.isnumber(node.right):
                y = node.right
            elif self.isvariable(node.right):
                y = self.variables[node.right]
            # value, binary, or unary operator?
            if node.op is None:
                val = x
            elif node.op in self._operator.keys():
                if not (x is None or y is None):
                    val = self._operator[node.op](x, y)
            elif node.op in self._uoperator.keys():
                val = self._uoperator[node.op](y)
            else:
                raise TypeError("Unknown operator: %s"%(node.op))  
                # should have been captured while parsing
        elif self.isvariable(node):
            val = self.variables[node]
        else:
#            print "EVALUATE non-node: ",node
            val = node   # isnumber
        return val


    def evaluate(self, node=None, variables=None):
        """Evaluate the mathematical expression numerically.
        If variables are provided as dictionary, they will supersede the default values."""
        val = None
        if not self._resolved:
            self.resolve()
        if node is None:
            node = self._root
        # *** MUST ADD handling of variables argument! ***
        self._check_undefined_variables()
        val = self._evaluate(node)
        return val


    def get_default(self, varname):
        return self._defaults.get(varname, None)

    
    def set_variable(self, ignore_error=False, **kwargs):
        """Set variable values. Variables can be given as one dict or in keyword
        syntax. An error will be raised if a variable name is not present in the
        object's variable list.
        Examples:
        d = {"x":5., "y":-1}
        tree.set_variable(d)
        OR:
        tree.set_variable(x=5., y=-1)"""
        if not self._resolved:
            self.resolve()
        for k, v in kwargs.items():
            if k in self._variables.keys():
                self._variables[k] = v
            elif not ignore_error:
                raise KeyError("Variable %s not defined!" % (k))


    # --- algebra ---
    # -   cleanup   -
    def _remove_atoms(self, x):
        """Eliminate mathNode with no operator. According to the tree building
        principles, this implies that there may only be a left value."""
        if self.isnode(x) and x.op is None:
            x = x.left
        return x

    
    def _remove_mult_zero(self, x):
        """Remove node x if it contains multiplication with the numerical value 0."""
        if self.isnode(x) and x.op is "*":
            if self.isnumber(x.left) and np.abs(x.left)<=self._tiny: 
                x = 0.
            elif self.isnumber(x.right) and np.abs(x.right)<=self._tiny: 
                x = 0.
        return x


    def _remove_div_zero(self, x):
        """Remove node x if it contains division of 0 by something.
        NOTE: strictly speaking this eliminates the possibility of 0/0 which may
        not always be desired, but is fine for the intended application of this class."""
        if self.isnode(x) and x.op is "/":
            if self.isnumber(x.left) and np.abs(x.left)<=self._tiny: 
                x = 0.
        return x


    def _remove_mod_zero(self, x):
        """Remove node x if it contains 0 modulo something."""
        if self.isnode(x) and x.op is "%":
            if self.isnumber(x.left) and np.abs(x.left)<=self._tiny: 
                x = 0.
        return x


    def _remove_mult_one(self, x):
        """Remove node x if it contains multiplication with the numerical value 1."""
        if self.isnode(x) and x.op is "*":
            if self.isnumber(x.left) and np.abs(x.left-1.)<=self._eps: 
                x = x.right
            elif self.isnumber(x.right) and np.abs(x.right-1.)<=self._eps: 
                x = x.left
        return x


    def _remove_divby_one(self, x):
        """Remove node x if it contains division by 1."""
        if self.isnode(x) and x.op is "/":
            if self.isnumber(x.right) and np.abs(x.right-1.)<=self._eps: 
                x = x.left
        return x


    def _remove_add_zero(self, x):
        """Remove node x if it contains addition with 0."""
        if self.isnode(x) and x.op is "+":
            if self.isnumber(x.left) and np.abs(x.left)<=self._tiny: 
                x = x.right
            elif self.isnumber(x.right) and np.abs(x.right)<=self._tiny: 
                x = x.left
        return x


    def _remove_sub_zero(self, x):
        """Remove node x if it contains subtraction of 0."""
        if self.isnode(x) and x.op is "~":
            if self.isnumber(x.right) and np.abs(x.right)<=self._tiny: 
                x = x.left
        return x


    def _remove_subfrom_zero(self, x):
        """Change '0-x' to '-1*x'."""
        if self.isnode(x) and x.op is "~":
            if self.isnumber(x.left) and np.abs(x.left)<=self._tiny:
                x.left = -1.
                x.op = "*"
        return x


    def _remove_num_ops(self, x):
        """Remove node x if it contains an operation with only numerical values."""
        if self.isnode(x):
            if x.left is None and self.isnumber(x.right):
                # evaluate unary function
                x = self._uoperator[x.op](x.right)
            elif self.isnumber(x.left) and self.isnumber(x.right): 
                x = self._operator[x.op](x.left, x.right)
        return x


    def _rearrange_left_right(self, x):
        """Arrange node elements so that factors tend to be left of variables and
        variables left of nodes. This must of course respect commutation laws."""
        if self.isnode(x) and not self.isnumber(x.left) and not x.left is None:
            canswap = x.op in ["+", "*"]
            shouldswap = self.isnumber(x.right)
            #  or (self.isnode(x.left) and self.isvariable(x.right))
            if canswap and shouldswap:
                x.swap_branches()
        return x


    def _sort_variables(self, x):
        """If there are two variables in a node, sort them alphabetically if the operator
        permits."""
        if self.isnode(x) and self.isvariable(x.left) and self.isvariable(x.right):
            canswap = x.op in ["+", "*"]
            if canswap:
                if x.right < x.left:
                    x.swap_branches()
        return x


    def cleanup(self, node=None, recursion=True):
        """Perform a series of cleanup operations for underlying nodes. This should
        be done after any algebraic operation to remove 'dead material'."""
        if node is None:
            node = self._root
            branchlist = ["left", "right", "root"]
        else:
            branchlist = ["left", "right"]
        if not self.isnode(node):
            return
        # first left, then right branch
        for branch in branchlist:
            if branch == "left":
                if recursion:
                    if self.isnode(node.left):
                        self.cleanup(node.left)
                x = node.left
            elif branch == "right":
                if recursion:
                    if self.isnode(node.right):
                        self.cleanup(node.right)
                x = node.right
            else:
                x = node
            # perform series of cleanup operations
            x = self._remove_atoms(x)
            x = self._remove_mult_zero(x)
            x = self._remove_div_zero(x)
            x = self._remove_mod_zero(x)
            x = self._remove_mult_one(x)
            x = self._remove_divby_one(x)
            x = self._remove_add_zero(x)
            x = self._remove_sub_zero(x)
            x = self._remove_subfrom_zero(x)
            if self._autoexecnumops:
                x = self._remove_num_ops(x)
            x = self._rearrange_left_right(x)
            x = self._sort_variables(x)
            # store result
            if branch == "left":
                node.left = x
            elif branch == "right":
                node.right = x
            elif branch == "root":    # special treatment of root node!
                if self.isnode(x):
                    self._root = x
                else:
                    self._root = mathNode( (x, None, None) )
            

    # -   simplify  -
    def _lrr_to_llr(self, x, changed=False):
        """Transform pattern 'a op (b op x)' to '(a op b) op x', where a and b
        are either numerical values or variables (i.e. strings) and x is a mathNode.
        For example, '2*(3*x)' will become '(2*3)*x', which can then be truncated
        to '6*x' during the final cleanup() operation.
        Note: cleanup should have been called before in order to have factors and
        variables to the left of mathNodes where possible."""
        if self.isvalue(x.left) and \
           self.isnode(x.right) and \
           self.isnumber(x.right.left) and \
           self.rank(x.left) >= self.rank(x.right.left) and \
           self.rank(x.right.right) > self.rank(x.right.left):
            cops = x.op+x.right.op
            nops = { "++":"++",    # translate current operators into new ones
                     "+~":"~+",
                     "~+":"~~",
                     "~~":"+~",
                     "**":"**",
                     "*/":"/*",
                     "/*":"//",
                     "//":"*/" }
            if cops in nops:
                # create a new node on the left branch and remove node from the right branch
                x.left = mathNode( (x.left, nops[cops][1], x.right.left) )
                x.op = nops[cops][0]
                x.right = x.right.right
                changed = True
        return x, changed


    def _lrr_to_llr2(self, x, changed=False):
        """Transform pattern 'a op (x op b)' to '(a op b) op x', where a and b
        are either numerical values or variables (i.e. strings) and x is a mathNode.
        This is only relevant if the operator near x is either '~' or '/'. 
        For example, '3~(x~2)' will become '(3+2)~x', which can then be truncated
        to '5~x' during the final cleanup() operation.
        Note: cleanup should have been called before in order to have factors and
        variables to the left of mathNodes where possible."""
        if self.isvalue(x.left) and \
           self.isnode(x.right) and \
           self.isnumber(x.right.left) and \
           self.rank(x.left) >= self.rank(x.right.right) and \
           self.rank(x.right.left) > self.rank(x.right.right):
            cops = x.op+x.right.op
            nops = { "+~":"+~",    # translate current operators into new ones
                     "~~":"~+",
                     "*/":"/*",
                     "//":"/*" }
            if cops in nops:
                # create a new node on the left branch and remove node from the right branch
                x.left = mathNode( (x.left, nops[cops][1], x.right.right) )
                x.op = nops[cops][0]
                x.right = x.right.left
                changed = True
        return x, changed


    def _llr_to_llr(self, x, changed=False):
        """Transform pattern '(a op x) op b' to '(a op b) op x', where a and b
        are either numerical values or variables (i.e. strings) and x is a mathNode.
        This is relevant only for subtraction and division.
        For example, '(2-x)+3' will become '(2+3)-x', which can then be truncated
        to '5-x' during the final cleanup() operation.
        Note: cleanup should have been called before in order to have factors and
        variables to the left of mathNodes where possible."""
        if self.isnode(x.left) and  \
           self.isvalue(x.left.left) and  \
           self.isvalue(x.right) and \
           self.rank(x.right) < self.rank(x.left.right):
            cops = x.op+x.left.op
            nops = { "~+":"+~",    # translate current operators into new ones
                     "~~":"~~",
                     "/*":"*/",
                     "//":"//" }
            if cops in nops:
                # modify node on the left branch
                tmp = x.right
                x.right = x.left.right
                x.left.right = tmp
                x.left.op = nops[cops][1]
                x.op = nops[cops][0]
                changed = True
        return x, changed


    def _llr_to_lrr(self, x, changed=False):
        """Transform pattern '(x op a) op b' to 'x op (a op b)', where a and b
        are either numerical values or variables (i.e. strings) and x is a mathNode.
        This is relevant only for subtraction and division.
        For example, '(x/6)/3' will become 'x/(6*3)', which can then be truncated
        to 'x/18' during the final cleanup() operation.
        Note: cleanup should have been called before in order to have factors and
        variables to the left of mathNodes where possible."""
        if self.isnode(x.left) and  \
           self.isvalue(x.left.right) and  \
           self.isvalue(x.right) and \
           self.rank(x.right) < self.rank(x.left.left):
            cops = x.op+x.left.op
            nops = { "~~":"~+",    # translate current operators into new ones
                     "//":"/*" }
            if cops in nops:
                # create a new node on the right branch and remove node from the left branch
                x.right = mathNode( (x.left.right, nops[cops][1], x.right) )
                x.op = nops[cops][0]
                x.left = x.left.left
                changed = True
        return x, changed


    def _move_node_to_left(self, x, changed=False):
        """Insert a node from a right branch into the left branch if permitted.
        Hence, a pattern like 'x op (y op z)' will become '(x op y) op z'. This only
        works for multiplication and addition on the upper node and will only be done
        if either x and y are numbers or none of them.
        This operation facilitates commutation and other functions."""
        if self.isnode(x.right) and \
           ((self.isnumber(x.left) and self.isnumber(x.right.left)) or \
           not (self.isnumber(x.left) or self.isnumber(x.right.left))):
            cops = x.op+x.right.op
            nops = { "++":"++",    # translate current operators into new ones
                     "+~":"~+",
                     "~+":"~~",
                     "~~":"+~",
                     "**":"**",
                     "*/":"/*",
                     "/*":"//",
                     "//":"*/" }
            if cops in nops:
                # create a new node on the left branch and remove node from the right branch
                x.left = mathNode( (x.left, nops[cops][1], x.right.left) )
                x.op = nops[cops][0]
                x.right = x.right.right
                changed = True
        return x, changed

    # for _move_node_to_right the nops translation table would be:
    #        nops = { "++":"++",    # translate current operators into new ones
    #                 "+~":"+~",
    #                 "~+":"+~",
    #                 "~~":"~+",
    #                 "**":"**",
    #                 "*/":"*/",
    #                 "/*":"*/",
    #                 "//":"/*" }

    
    def _extract_factor(self, x, changed=False):
        """Extract a numerical factor from a term such as '(a*x)*y' or '(a*x)/y'.
        The resulting term will be 'a*(x*y)' or 'a*(x/y)', respectively."""
        if x.op is not None and \
                x.op in "*/" and \
                self.isnode(x.left) and \
                self.isnumber(x.left.left) and \
                x.left.op == "*":
            # create a new node on the right branch and remove node from the left branch
            x.right = mathNode( (x.left.right, x.left.op, x.right) )
            x.op = "*"
            x.left = x.left.left
            changed = True
        return x, changed


    def _remove_double_negative(self, x, changed=False):
        """Change pattern '...+ (-number)*x' to '...- number*x' and
        '...- (-number) * x' to '...+ number*x'."""
        if self.isnode(x.right) and \
                self.isnumber(x.right.left) and \
                x.right.left < 0. and \
                x.op in '+~' and \
                x.right.op in '*/':
            x.right.left *= -1.
            x.op = '+' if x.op == '~' else '~'  # change operator
            changed = True
        return x, changed


    def simplify(self, node=None, recursion=True):
        """Perform a series of algebraic operations to combine factors and move
        numerical values or variables to the left as far as possible."""
        if node is None:
            node = self._root
        if not self.isnode(node):
            return
        # recursion: first left, then right branch
        if recursion:
            if self.isnode(node.left):
                self.simplify(node.left)
            if self.isnode(node.right):
                self.simplify(node.right)
        # perform series of cleanup operations
        # each of these must return x unchanged if the conditions don't apply
        x = node
        changed = False
        x, changed = self._lrr_to_llr(x, changed)
        x, changed = self._lrr_to_llr2(x, changed)
        x, changed = self._llr_to_llr(x, changed)
        x, changed = self._llr_to_lrr(x, changed)
        x, changed = self._extract_factor(x, changed)
        x, changed = self._move_node_to_left(x, changed)
        x, changed = self._remove_double_negative(x, changed)
        # store result
        node.left = x.left
        node.op = x.op
        node.right = x.right
        # cleanup what we have done
        self.cleanup(node, recursion=False)
        # and do it again if anything changed
        if changed:
            self.simplify(node, recursion=recursion)


    # -   operations   -
    def _add_term_factors(self, node):
        """Look for terms (nodes, numbers, or variables) below a node with a '+' or '~' operator,
        which itself is not another node with a '+' or '~' operator. If this term has the form
        'anything / number' convert to '1/number * anything', and if it is not 'number * anything'
        convert it into this form by adding a new node with '1.0 * anything'. Finally, if node.op is '~'
        change to '+' and multiply the factor of the right branch by -1.
        This is used for the combination of terms and will be reverted automatically upon cleanup()
        if needed."""
        if node is None:
            node = self._root
        if self.isnode(node):
            if self.isnode(node.left):
                self._add_term_factors(node.left)
            if self.isnode(node.right):
                self._add_term_factors(node.right)
            if node.op is not None and node.op in '+~':
                # check left branch
                if not (self.isnode(node.left) and node.left.op in "+~"):
                    # check for division by number
                    if self.isnode(node.left) and \
                       node.left.op == "/" and \
                       self.isnumber(node.left.right):
                        node.left.swap_branches()
                        node.left.left = 1./node.left.left
                        node.left.op = "*"
                    # check for multiplication of number
                    if not (self.isnode(node.left) and \
                            node.left.op == "*" and \
                            self.isnumber(node.left.left)):
                        # add a new factor*term node
                        node.left = mathNode( (1., "*", node.left) )
                # check right branch
                if not (self.isnode(node.right) and node.right.op in "+~"):
                    # check for division by number
                    if self.isnode(node.right) and \
                       node.right.op == "/" and \
                       self.isnumber(node.right.right):
                        node.right.swap_branches()
                        node.right.left = 1./node.right.left
                        node.right.op = "*"
                    # check for multiplication of number
                    if not (self.isnode(node.right) and \
                            node.right.op == "*" and \
                            self.isnumber(node.right.left)):
                        # add a new factor*term node
                        node.right = mathNode( (1., "*", node.right) )
                    # multiply factor by -1 and change operator if node.op is '~'
                    if node.op == '~':
                        node.op = '+'
                        node.right.left *= -1.
                        
        
    def _add_terms(self, n1, n2):
        """Perform an addition of two subnodes from the nodelist.
        The second term will then be set to zero."""
        term1, factor1, node1, branch1 = n1
        term2, factor2, node2, branch2 = n2
        if factor1 is None or factor2 is None:
            print "**** None factor!! factor1, factor2, n1, n2 : ", factor1, factor2, n1, n2
        f1 = factor1 if not factor1 is None else 1.0
        f2 = factor2 if not factor2 is None else 1.0
        # insert new factor or update factor value at first node
        if factor1 is None:    # no factor present for term1 -> insert new node
#            print "... inserting node in branch %i"%(branch1), "***SHOULDN'T OCCUR! ***"
            if branch1 < 0:
                node1.left = mathNode((f1 + f2, "*", node1.left))   
            else:
                node1.right = mathNode((f1 + f2, "*", node1.right))
        else:
#            print "... updating factor at node %s"%(node1.__repr__()[-8:-2])
            if branch1 < 0:
                node1.left.left = f1 + f2   # must have been a numerical value before
            else:
                node1.right.left = f1 + f2
        # remove subtree from second node and set to zero
        if branch2 < 0:
            node2.left = 0.
        else:
            node2.right = 0.
        return f1 + f2
            

    def _build_nodelist_t(self, node, sign=1.):
        """Establish a list of nodes that are connected via '+' or '~' and have children
        which are not again nodes with '+'. Then extract potential numerical factors.
        Sign is passed as +1 or -1 depending on the last term on the parent level."""
        def nl_element(x, parent, sign=1., branch=1):
            """Compose one nodelist element once a suitable term has been found."""
            # check if we can extract a numerical factor
            if self.isnode(x) and x.op == "*" and self.isnumber(x.left):
                factor = sign * x.left
                term = str(x.right)
            else:
                factor = None
                term = str(x)
            return (term, factor, parent, branch)
            
        res = []
        op = "+~"
        if self.isnode(node) and node.op in op:
            # check left side
            if self.isnode(node.left) and node.left.op in op:
                tmp = self._build_nodelist_t(node.left, sign)
                if len(tmp)>0:
                    res.extend(tmp)
            elif node.right is not None:
                newitem = nl_element(node.left, node, sign, -1)
                if newitem[1] is not None:
                    res.append(newitem)
            # check right side
            if node.op == "~":
                sign *= -1.
            if self.isnode(node.right) and node.right.op in op:
                tmp = self._build_nodelist_t(node.right, sign)
                if len(tmp)>0:
                    res.extend(tmp)
            elif node.right is not None:
                newitem = nl_element(node.right, node, sign, +1)
                if newitem[1] is not None:
                    res.append(newitem)
        return res
                

    def _combine_terms(self, node=None, recursion=True):
        """Combine equal terms with optional factors.
        This method establishes a list of nodes which have a numerical factor on
        the left side and anything on the right side. If the righthand terms have the
        same string representation, they can be combined.
        Users should call the combine_terms interface routine."""
        if self.isnode(node) and recursion:
            self._combine_terms(node.left)
            self._combine_terms(node.right)
        if self.isnode(node) and node.op == "+":     #### how about '~'??
            # build list of terms in question
            nodelist = self._build_nodelist_t(node)
##            print "nodelist for node ", node
##            for i,n in enumerate(nodelist):
##                term1, factor1, node1, branch1 = n
##                if factor1 is not None:
##                    print "%i: %10.2f %24s %3i"%(i,factor1,term1,branch1)
##                else:
##                    print "%i: None %24s %3i"%(i,term1,branch1)
            for i, n in enumerate(nodelist):
                term1, factor1, node1, branch1 = n
                if term1 is None:
                    continue
                # check for equal term (string representation)
                for j in range(i+1, len(nodelist)):
                    term2, factor2, node2, branch2 = nodelist[j]
                    if term1 == term2:
                        # add factor and modify tree, update nodelist
                        newfac1 = self._add_terms(nodelist[i], nodelist[j])
                        # mark nodelist[j] as done
                        nodelist[j] = (None, None, None, None)


    def _factorize(self, node=None, recursion=True):
        """Attempt to factorize the term by 'exchanging' lower level '+' or '~' with
        higher level '*'. This is the actual factorization routine. To call it, use
        the factorize interface method."""
        if self.isnode(node) and recursion: 
            # dig deeper
            self._factorize(node.left)
            self._factorize(node.right)
        if self.isnode(node) and node.op == "*": 
            # check left side
            if self.isnode(node.left) and node.left.op in "+~":
                node.op = node.left.op
                node.left = mathNode((node.left.left, "*", node.left.right))
                rightnode = node.right
                node.right = mathNode((node.left.right, "*", rightnode))
                node.left.right = rightnode
                self._factorize(node)
            # check right side
            elif self.isnode(node.right) and node.right.op in "+~":
                node.op = node.right.op
                node.right = mathNode((node.right.left, "*", node.right.right))
                leftnode = node.left
                node.left = mathNode((leftnode, "*", node.right.left))
                node.right.left = leftnode
                self._factorize(node)


    def combine_terms(self, node=None):
        """Combine equal terms with optional factors."""
        if not self._resolved:
            self.resolve()
        if node is None:
            node = self._root
        if self.isnode(node): 
            # must set _autoexecnumops to true for term combination
            self._autoexecnumops = True
            # simplify term to increase chances for combining terms
            self.simplify(node)
            # add numerical factors where there are none
            self._add_term_factors(node)
            # combine terms where possible
            self._combine_terms(node)
            # cleanup
            self.simplify(node)
            self.cleanup()
            # rebuild variable list and copy previously defined variable values
            oldvars = self.variables
            self._variables = {}
            self.resolve()
            for v in self.variables:
                if v in oldvars:
                    self._variables[v] = oldvars[v]
            

    def factorize(self, node=None, recursion=True):
        """Attempt to factorize the term by 'exchanging' lower level '+' or '~' with
        higher level '*'. This is the interface routine which the user should call.
        The actual work happens in the internal _factorize method."""
        if not self._resolved:
            self.resolve()
        if node is None:
            node = self._root
        # must set _autoexecnumops to true for factorisation
        self._autoexecnumops = True
        # simplify term to increase chances for factorisation
        self.simplify(node)
        # call factorization
        self._factorize(node, recursion=recursion)
        self.combine_terms(node)


#
# ==== TEST SUITE ====
#
def test(term, val):
    t = mathTree(term)
    t.resolve()
    t.set_variable(E=np.e, PI=np.pi, ignore_error=True)
    vtest = t.evaluate()
    if np.abs(vtest-val) < 1.e-9:
        print "test %s successful: result = %g" % (term,vtest)
    else:
        print "!!!! test %s not successful! Should be %g is %g." % (term,val,vtest)


def testsuite_eval():
    print
    print "MATHNODE:"
    print "TESTING EVALUATE..."
    test( "9", 9 )
    test( "-9", -9 )
    test( "--9", 9 )
    test( "-E", -np.e )
    test( "E-12", np.e - 12 )
    test( "-E-12", -np.e - 12 )
    test( "9 + 3 + 6", 9 + 3 + 6 )
    test( "9 + 3 / 11", 9 + 3.0 / 11 )
    test( "(9 + 3)", (9 + 3) )
    test( "(9+3) / 11", (9+3.0) / 11 )
    test( "9 - 12 - 6", 9 - 12 - 6 )
    test( "9 - (12 - 6)", 9 - (12 - 6) )
    test( "7.*(8.+9.)-10.*(11-12)+(13+14)*15", 7.*(8.+9.)-10.*(11-12)+(13+14)*15)
    test( "2*3.14159", 2*3.14159 )
    test( "3.1415926535*3.1415926535 / 10", 3.1415926535*3.1415926535 / 10 )
    test( "2.4e-12*exp(-1240./298.)", 2.4e-12*np.exp(-1240./298.) )
    test( "2.4e+12*exp(-8240./298.)", 2.4e+12*np.exp(-8240./298.) )
    test( "PI * PI / 10", np.pi * np.pi / 10 )
    test( "PI*PI/10", np.pi*np.pi/10 )
    test( "PI^2", np.pi**2 )
    test( "round(PI^2)", round(np.pi**2) )
    test( "6.02E23 * 8.048", 6.02E23 * 8.048 )
    test( "e / 3", np.e / 3 )
    test( "sin(PI/2)", np.sin(np.pi/2) )
    test( "trunc(E)", int(np.e) )
    test( "trunc(-E)", int(-np.e) )
    test( "ceil(E)", np.ceil(np.e) )
    test( "ceil(-E)", np.ceil(-np.e) )
    test( "round(E)", round(np.e) )
    test( "round(-E)", round(-np.e) )
    test( "E^PI", np.e**np.pi )
    test( "2^3^2", 2**3**2 )
    test( "2^(3^2)", 2**(3**2) )
    test( "(2^3)^2", (2**3)**2 )
    test( "2^3+2", 2**3+2 )
    test( "-2^9", -2**9 )
    test( "sign(-2)", -1 )
    test( "sign(0)", 0 )
    test( "sign(0.1)", 1 )
    test( "r2d(d2r(pi))", np.pi )
    print
    print "TEST COMPLETED."


def test_factorisation(term):
    t = mathTree(term)
    t.resolve()
    x = np.random.uniform(low=-1.e6, high=1.e6)
    y = np.random.uniform(low=-1.e6, high=1.e6)
    z = np.random.uniform(low=-1.e6, high=1.e6)
    t.set_variable(x=x, y=y, z=z, ignore_error=True)
    val = t.evaluate()   # based on testsuite_evaluate we assume that this works!
    # now factorize and simplify
    t.factorize()
    vtest = t.evaluate()
    reqprec = 10.**(np.log10(np.abs(val))-14)
    print "Value %g, required precision %g" % (val,reqprec)
    if np.abs(vtest-val) < reqprec:
        print "test of term %s successful: resulting expression = %s" % (term,str(t))
    else:
        print "!!!! test of term %s not successful! Expression %s." % (term,t._root)
        print "result before factorization = %f, and after %f" % (val,vtest)
    # now also test string functionality
    t2 = mathTree(str(t))            # convert to string and build new tree
    t2.set_variable(**t.variables)  # clone variable values
    vtest2 = t2.evaluate()
    if np.abs(vtest-vtest2) > reqprec:
        print "!!!! test part 2 (string conversion) not successful!"
        print "     Original term = %s" % (term)
        print "     String representation 1 = %s" % (str(t))
        print "     String representation 2 = %s" % (str(t2))
        print "     Value 1 = %14.9g, value 2 = %14.9g" % (vtest, vtest2)
        
        
def testsuite_factorisation():
    print
    print "MATHNODE:"
    print "TESTING FACTORIZE..."
    test_factorisation( "x" )
    test_factorisation( "(x+y)" )
    test_factorisation( "1*(x+y)" )
    test_factorisation( "1*(x-y)" )
    test_factorisation( "-1*(x-y)" )
    test_factorisation( "(x-y)+3*(x+y)" )
    test_factorisation( "(x-y)+3*(x+y)-2*(y-z)+5*x+9*(x+z)" )
    test_factorisation( "4*(x*x-y)+3*(x+y*y)" )
    test_factorisation( "2*sin(x)-4*cos(x)+0.5*(sin(x)-cos(x))" )
    test_factorisation( "4.*pi*sqrt(abs(8*(x+y)+6.5*x^2+e*(y-x)))" )
    test_factorisation( "2*(x+4*(x-3*(x+1.*(x-25.))))" )
    test_factorisation( "4+x*(3+x*(1-x*(25+x)))" )
    test_factorisation( "(x^3+y^3)*(x-y)" )
    test_factorisation( "(x+y)^2" )
    print
    print "TEST COMPLETED."


if __name__ == "__main__":
#    import sys
#    sys.setrecursionlimit(60)
    pass

#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# Problem Writer for CPLEX LP Format Files
#

import logging
import math
import weakref

from six import iterkeys, itervalues, iteritems, advance_iterator
from six.moves import xrange, zip

from coopr.opt import ProblemFormat
from coopr.opt.base import AbstractProblemWriter
from coopr.pyomo.base import SymbolMap, TextLabeler, NumericLabeler
from coopr.pyomo.base import BooleanSet, Constraint, ConstraintList, expr, IntegerSet, Component
from coopr.pyomo.base import active_subcomponents_generator, active_subcomponents_data_generator
from coopr.pyomo.base import Var, value, label_from_name, NumericConstant, Suffix
from coopr.pyomo.base.sos import SOSConstraint
from coopr.pyomo.base.objective import Objective, minimize, maximize
from coopr.pyomo.expr import canonical_degree, LinearCanonicalRepn

from pyutilib.component.core import alias
from pyutilib.misc import tostr, PauseGC

logger = logging.getLogger('coopr.pyomo')

class ProblemWriter_cpxlp(AbstractProblemWriter):

    alias('cpxlp')
    alias('lp')

    def __init__(self):

        AbstractProblemWriter.__init__(self, ProblemFormat.cpxlp)

        # the LP writer is responsible for tracking which variables are
        # referenced in constraints, so that one doesn't end up with a
        # zillion "unreferenced variables" warning messages. stored at
        # the object level to avoid additional method arguments.
        # collection of id(_VarData).
        self._referenced_variable_ids = set()
        
        # Keven Hunter made a nice point about using %.16g in his attachment
        # to ticket #4319. I am adjusting this to %.17g as this mocks the
        # behavior of using %r (i.e., float('%r'%<number>) == <number>) with
        # the added benefit of outputting (+/-). The only case where this
        # fails to mock the behavior of %r is for large (long) integers (L),
        # which is a rare case to run into and is probably indicative of
        # other issues with the model.
        # *** NOTE ***: If you use 'r' or 's' here, it will break code that
        #               relies on using '%+' before the formatting character
        #               and you will need to go add extra logic to output
        #               the number's sign.
        self._precision_string = '.17g'

    def __call__(self, model, output_filename, solver_capability, io_options):

        # NOTE: io_options is a simple dictionary of keyword-value pairs
        #       specific to this writer. 
        symbolic_solver_labels = io_options.pop("symbolic_solver_labels", False)
        output_fixed_variable_bounds = io_options.pop("output_fixed_variable_bounds", False)
        if io_options:
            logger.warn(
                "ProblemWriter_cpxlp passed unrecognized io_options:\n\t" +
                "\n\t".join("%s = %s" % (k,v) for k,v in iteritems(io_options)))

        # when sorting, there are a non-trivial number of temporary objects
        # created. these all yield non-circular references, so disable GC -
        # the overhead is non-trivial, and because references are non-circular,
        # everything will be collected immediately anyway.
        suspend_gc = PauseGC()

        # clear the collection of referenced variables.
        self._referenced_variable_ids.clear()

        if output_filename is None:
            output_filename = model.name + ".lp"

        output_file=open(output_filename, "w")
        symbol_map = self._print_model_LP(model, output_file, solver_capability, symbolic_solver_labels, output_fixed_variable_bounds)
        output_file.close()

        return output_filename, symbol_map

    def _get_bound(self, exp):

        if exp.is_fixed():
            return exp()
        else:
            raise ValueError("ERROR: non-fixed bound: " + str(exp))

    def _print_expr_linear(self, x, output_file, object_symbol_dictionary, is_objective, output_fixed_variable_bounds):

        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo linear encoding of an expression to write in LP format
        """

        # Currently, it appears that we only need to print the constant
        # offset term for objectives.
        print_offset = is_objective

        constant_term = x[0]
        linear_terms = x[1]

        name_to_coefficient_map = {}

        for coefficient, var_value in linear_terms:

            if (var_value.fixed and (not output_fixed_variable_bounds)):

                constant_term += (coefficient * var_value.value)

            else:

                var_id = id(var_value)
                if var_id not in self._referenced_variable_ids:
                    self._referenced_variable_ids.add(var_id)

                name = object_symbol_dictionary[id(var_value)]

                # due to potential disabling of expression simplification,
                # variables might appear more than once - condense coefficients.
                name_to_coefficient_map[name] = coefficient + name_to_coefficient_map.get(name,0.0)

        sorted_names = sorted(iterkeys(name_to_coefficient_map))

        string_template = '%+'+self._precision_string+' %s\n'
        for name in sorted_names:

            coefficient = name_to_coefficient_map[name]

            output_file.write(string_template % (coefficient, name))

        if print_offset and (constant_term != 0.0):

            output_file.write(string_template % (constant_term, 'ONE_VAR_CONSTANT'))

        return constant_term


    def _print_expr_canonical(self, x, output_file, object_symbol_dictionary, is_objective):

        """
        Return a expression as a string in LP format.

        Note that this function does not handle any differences in LP format
        interpretation by the solvers (e.g. CPlex vs GLPK).  That decision is
        left up to the caller.

        required arguments:
          x: A Pyomo canonical expression to write in LP format
        """

        # cache - this is referenced numerous times.
        if isinstance(x, LinearCanonicalRepn):
            var_hashes = None # not needed
        else:
            var_hashes = x[-1]

        #
        # Linear
        #
        linear_coef_string_template = '%+'+self._precision_string+' %s\n'
        if isinstance(x, LinearCanonicalRepn) and (x.linear is not None):

            # the 99% case is when the input instance is a linear canonical expression, so the exception should be rare.
            for i in xrange(0,len(x.linear)):
                var_coef = x.linear[i]
                var_data = x.variables[i]
                if id(var_data) not in self._referenced_variable_ids:
                    self._referenced_variable_ids.add(id(var_data))

            sorted_names = [(object_symbol_dictionary[id(x.variables[i])], x.linear[i]) for i in xrange(0,len(x.linear))]
            sorted_names.sort()

            for name, coef in sorted_names:
                output_file.write(linear_coef_string_template % (coef, name))
        elif 1 in x:

            for var_hash in x[1]:
                var_id = id(var_hashes[var_hash])
                if var_id not in self._referenced_variable_ids:
                    self._referenced_variable_ids.add(var_id)  

            sorted_names = [(object_symbol_dictionary[id(var_hashes[var_hash])], var_coefficient) for var_hash, var_coefficient in iteritems(x[1])]
            sorted_names.sort()

            for name, coef in sorted_names:
                output_file.write(linear_coef_string_template % (coef, name))

        #
        # Quadratic
        #
        quad_coef_string_template = '%+'+self._precision_string+' '
        if canonical_degree(x) is 2:

            # first, make sure there is something to output - it is possible for all
            # terms to have coefficients equal to 0.0, in which case you don't want
            # to get into the bracket notation at all.
            # NOTE: if the coefficient is really 0.0, it should be preprocessed out by
            #       the canonial expression generator!
            found_nonzero_term = False # until proven otherwise
            for var_hash, var_coefficient in iteritems(x[2]):
                for var in var_hash:
                    var_value = var_hashes[var]
                    var_id = id(var_value)
                    if var_id not in self._referenced_variable_ids:
                        self._referenced_variable_ids.add(var_id)
                    
                if math.fabs(var_coefficient) != 0.0:
                    found_nonzero_term = True
                    break

            if found_nonzero_term:

                output_file.write("+ [\n")

                num_output = 0

                for var_hash in sorted(iterkeys(x[2])):

                    coefficient = x[2][var_hash]

                    if is_objective:
                        coefficient *= 2

                    # times 2 because LP format requires /2 for all the quadratic
                    # terms /of the objective only/.  Discovered the last bit thru
                    # trial and error.  Obnoxious.
                    # Ref: ILog CPlex 8.0 User's Manual, p197.

                    output_file.write(quad_coef_string_template % coefficient)
                    term_variables = []

                    for var in var_hash:
                        var_value = var_hashes[var]
                        name = object_symbol_dictionary[id(var_value)]
                        term_variables.append(name)

                    if len(term_variables) == 2:
                        output_file.write("%s * %s" % (term_variables[0],term_variables[1]))
                    else:
                        output_file.write("%s ^ 2" % term_variables[0])
                    output_file.write("\n")

                output_file.write("]")

                if is_objective:
                    output_file.write(' / 2\n')
                    # divide by 2 because LP format requires /2 for all the quadratic
                    # terms.  Weird.  Ref: ILog CPlex 8.0 User's Manual, p197
                else:
                    output_file.write("\n")


        #
        # Constant offset
        #
        if isinstance(x, LinearCanonicalRepn):
            constant = x.constant
        else:
            if 0 in x:
                constant = x[0][None]
            else:
                constant = None

        if constant is not None:
            offset = constant
        else:
            offset=0.0

        # Currently, it appears that we only need to print the constant
        # offset term for objectives.
        obj_string_template = '%+'+self._precision_string+' %s\n'
        if is_objective and offset != 0.0:
            output_file.write(obj_string_template % (offset, 'ONE_VAR_CONSTANT'))

        #
        # Return constant offset
        #
        return offset

    def printSOS(self, symbol_map, labeler, soscondata, output_file):
        """
        Prints the SOS constraint associated with the _SOSConstraintData object
        """

        Vars = soscondata.get_members()
        Weights = soscondata.get_weights()
        Level = soscondata.get_level()

        if (Vars is None) or (len(Vars) == 0):
            return

        output_file.write('%s: S%s::\n' % (symbol_map.getSymbol(soscondata,labeler), Level))

        sos_template_string = "%s:%"+self._precision_string+"\n"
        for vardata, weight in zip(Vars, Weights):
            self._referenced_variable_ids.add(id(vardata))
            output_file.write(sos_template_string % (symbol_map.getSymbol(vardata,labeler), weight) )

    #
    # a simple utility to pass through each variable and constraint
    # in the input model and populate the symbol map accordingly. once
    # we know all of the objects in the model, we can then "freeze"
    # the contents and use more efficient query mechanisms on simple
    # dictionaries - and avoid checking and function call overhead.
    #
    def _populate_symbol_map(self, model, symbol_map, labeler):

        # NOTE: we use createSymbol instead of getSymbol because we know
        # whether or not the symbol exists, and don't want to the overhead
        # of error/duplicate checking.

        # cache frequently called functions
        create_symbol_func = SymbolMap.createSymbol
        create_symbols_func = SymbolMap.createSymbols
        alias_symbol_func = SymbolMap.alias

        for objective_data in active_subcomponents_data_generator(model, Objective):
            create_symbol_func(symbol_map, objective_data, labeler)

        for block in model.all_blocks(sort_by_keys=True):

            for constraint_data in active_subcomponents_data_generator(block, Constraint):

                constraint_data_symbol = create_symbol_func(symbol_map, constraint_data, labeler)
                if constraint_data._equality:
                    label = 'c_e_' + constraint_data_symbol + '_'
                    alias_symbol_func(symbol_map, constraint_data, label)
                else:
                    if constraint_data.lower is not None:
                        if constraint_data.upper is not None:
                            alias_symbol_func(symbol_map, constraint_data, 'r_l_' + constraint_data_symbol + '_')
                            alias_symbol_func(symbol_map, constraint_data, 'r_u_' + constraint_data_symbol + '_')
                        else:
                            label = 'c_l_' + constraint_data_symbol + '_'
                            alias_symbol_func(symbol_map, constraint_data, label)
                    elif constraint_data.upper is not None:
                        label = 'c_u_' + constraint_data_symbol + '_'
                        alias_symbol_func(symbol_map, constraint_data, label)
                        
            create_symbols_func(symbol_map, active_subcomponents_data_generator(block, Var), labeler)
            
            for con in active_subcomponents_data_generator(block,SOSConstraint):
                create_symbol_func(symbol_map, con, labeler)

    def _print_model_LP(self, model, output_file, solver_capability, symbolic_solver_labels, output_fixed_variable_bounds):

        symbol_map = SymbolMap(model)

        if symbolic_solver_labels is True:
            labeler = TextLabeler()
        else:
            labeler = NumericLabeler('x')

        # populate the symbol map in a single pass.
        self._populate_symbol_map(model, symbol_map, labeler)

        # and extract the information we'll need for rapid labeling.
        object_symbol_dictionary = symbol_map.getByObjectDictionary()

        # cache - these are called all the time.
        print_expr_linear = self._print_expr_linear
        print_expr_canonical = self._print_expr_canonical

        # print the model name and the source, so we know roughly where
        # it came from.
        #
        # NOTE: this *must* use the "\* ... *\" comment format: the GLPK
        # LP parser does not correctly handle other formats (notably, "%").
        output_file.write(
            "\\* Source Pyomo model name=%s *\\\n\n" % (model.name,) )

        #
        # Objective
        #
        model_repn_suffix = model.subcomponent("canonical_repn")
        if (model_repn_suffix is None) or (not model_repn_suffix.type() is Suffix) or (not model_repn_suffix.active is True):
            raise ValueError("Unable to find an active Suffix with name 'canonical_repn' on block: %s" % (model.cname(True)))

        _obj = list(active_subcomponents_data_generator(model,Objective))

        supports_quadratic_objective = solver_capability('quadratic_objective')

        numObj = len(_obj)
        if numObj == 0:
            msg = "ERROR: No objectives defined for input model '%s'; "    \
                  ' cannot write legal LP file'
            raise ValueError(msg % str( model.name ))
        if numObj > 1:
            msg = "More than one active objective defined for input model '%s'; " \
                  'Cannot write legal LP file\n'                           \
                  'Objectives: %s'
            raise ValueError(
                msg % ( model.name,', '.join("'%s'" % x.cname(True) for x in _obj) ))

        obj_data = _obj[0]
        symbol_map.alias(obj_data, '__default_objective__')
        if obj_data.is_minimizing():
            output_file.write("min \n")
        else:
            output_file.write("max \n")


        obj_data_repn = model_repn_suffix.getValue(obj_data)
        if obj_data_repn is None:
            raise RuntimeError("No canonical representation identified for objective="+obj_data.name)
        degree = canonical_degree(obj_data_repn)

        if degree == 0:
            print("Warning: Constant objective detected, replacing " +
                   "with a placeholder to prevent solver failure.")

            output_file.write(object_symbol_dictionary[id(obj_data)] \
                 + ": +0.0 ONE_VAR_CONSTANT\n")

            # Skip the remaining logic of the section
        else:
            if degree == 2:

                if not supports_quadratic_objective:
                    raise RuntimeError(
                        'Selected solver is unable to handle objective functions with quadratic terms. ' \
                        'Objective at issue: %s.' % obj_data.cname())

            elif degree != 1:
                msg  = "Cannot write legal LP file.  Objective '%s' "  \
                       'has nonlinear terms that are not quadratic.' % obj_data.cname(True)
                raise RuntimeError(msg)

            output_file.write(object_symbol_dictionary[id(obj_data)]+':\n')

            offset = print_expr_canonical( obj_data_repn,
                                                 output_file,
                                                 object_symbol_dictionary,
                                                 True )

        # Constraints
        #
        # If there are no non-trivial constraints, you'll end up with an empty
        # constraint block. CPLEX is OK with this, but GLPK isn't. And
        # eliminating the constraint block (i.e., the "s.t." line) causes GLPK
        # to whine elsewhere. output a warning if the constraint block is empty,
        # so users can quickly determine the cause of the solve failure.

        output_file.write("\n")
        output_file.write("s.t.\n")
        output_file.write("\n")

        have_nontrivial = False

        supports_quadratic_constraint = solver_capability('quadratic_constraint')

        # FIXME: This is a hack to get nested blocks working...
        eq_string_template = "= %"+self._precision_string+'\n'
        geq_string_template = ">= %"+self._precision_string+'\n\n'
        leq_string_template = "<= %"+self._precision_string+'\n\n'
        for block in model.all_blocks(sort_by_keys=True):

            block_repn_suffix = block.subcomponent("canonical_repn")
            if (block_repn_suffix is None) or (not block_repn_suffix.type() is Suffix) or (not block_repn_suffix.active is True):
                block_repn_suffix = None
            block_lin_body_suffix = block.subcomponent("lin_body")
            if (block_lin_body_suffix is None) or (not block_lin_body_suffix.type() is Suffix) or (not block_lin_body_suffix.active is True):
                block_lin_body_suffix = None

            for constraint in active_subcomponents_generator(block,Constraint):

                if constraint.trivial:
                    continue

                have_nontrivial=True

                for index in sorted(iterkeys(constraint)):

                    constraint_data = constraint[index]
                    if not constraint_data.active:
                        continue

                    # if expression trees have been linearized, then the canonical
                    # representation attribute on the constraint data object will
                    # be equal to None.
                    constraint_data_repn = None
                    if block_repn_suffix is not None:
                        constraint_data_repn = block_repn_suffix.getValue(constraint_data)
                    if constraint_data_repn is not None:

                        degree = canonical_degree(constraint_data_repn)

                        # There are conditions, e.g., when fixing variables, under which
                        # a constraint block might be empty.  Ignore these, for both
                        # practical reasons and the fact that the CPLEX LP format
                        # requires a variable in the constraint body.  It is also
                        # possible that the body of the constraint consists of only a
                        # constant, in which case the "variable" of
                        if degree == 0:
                            # this happens *all* the time in many applications,
                            # including PH - so suppress the warning.
                            #
                            #msg = 'WARNING: ignoring constraint %s[%s] which is ' \
                            #      'constant'
                            #print msg % (str(C),str(index))
                            continue

                        if degree == 2:
                            if not supports_quadratic_constraint:
                                msg  = 'Solver unable to handle quadratic expressions.'\
                                       "  Constraint at issue: '%s%%s'"
                                msg %= constraint.name
                                if index is None:
                                    msg %= ''
                                else:
                                    msg %= '%s' % ( str(index)
                                        .replace('(', '[')
                                        .replace(')', ']')
                                    )

                                raise ValueError(msg)

                        elif degree != 1:
                            msg = "Cannot write legal LP file.  Constraint '%s%s' "   \
                                  'has a body with nonlinear terms.'
                            if index is None:
                                msg %= ( constraint.name, '')
                            else:
                                msg %= ( constraint.name, '[%s]' % index )
                            raise ValueError(msg)

                    con_symbol = object_symbol_dictionary[id(constraint_data)]
                    if constraint_data._equality:
                        label = 'c_e_' + con_symbol + '_'
                        output_file.write(label+':\n')
                        lin_body = None
                        if block_lin_body_suffix is not None:
                            lin_body = block_lin_body_suffix.getValue(constraint_data)
                        if lin_body is not None:
                            offset = print_expr_linear(lin_body, output_file, object_symbol_dictionary, False, output_fixed_variable_bounds)
                        else:
                            offset = print_expr_canonical(constraint_data_repn, output_file, object_symbol_dictionary, False)
                        bound = constraint_data.lower
                        bound = self._get_bound(bound) - offset
                        output_file.write(eq_string_template%bound)
                        output_file.write("\n")
                    else:
                        lin_body = None
                        if block_lin_body_suffix is not None:
                            lin_body = block_lin_body_suffix.getValue(constraint_data)
                        if constraint_data.lower is not None:
                            if constraint_data.upper is not None:
                                label = 'r_l_' + con_symbol + '_'
                            else:
                                label = 'c_l_' + con_symbol + '_'
                            output_file.write(label+':\n')
                            if lin_body is not None:
                                offset = print_expr_linear(lin_body, output_file, object_symbol_dictionary, False, output_fixed_variable_bounds)
                            else:
                                offset = print_expr_canonical(constraint_data_repn, output_file, object_symbol_dictionary, False)
                            bound = constraint_data.lower
                            bound = self._get_bound(bound) - offset
                            output_file.write(geq_string_template%bound)
                        if constraint_data.upper is not None:
                            if constraint_data.lower is not None:
                                label = 'r_u_' + con_symbol + '_'
                            else:
                                label = 'c_u_' + con_symbol + '_'
                            output_file.write(label+':\n')
                            if lin_body is not None:
                                offset = print_expr_linear(lin_body, output_file, object_symbol_dictionary, False, output_fixed_variable_bounds)
                            else:
                                offset = print_expr_canonical(constraint_data_repn, output_file, object_symbol_dictionary, False)
                            bound = constraint_data.upper
                            bound = self._get_bound(bound) - offset
                            output_file.write(leq_string_template%bound)

        if not have_nontrivial:
            print('WARNING: Empty constraint block written in LP format '  \
                  '- solver may error')

        # the CPLEX LP format doesn't allow constants in the objective (or
        # constraint body), which is a bit silly.  To avoid painful
        # book-keeping, we introduce the following "variable", constrained
        # to the value 1.  This is used when quadratic terms are present.
        # worst-case, if not used, is that CPLEX easily pre-processes it out.
        prefix = ""
        output_file.write('%sc_e_ONE_VAR_CONSTANT: \n' % prefix)
        output_file.write('%sONE_VAR_CONSTANT = 1.0\n' % prefix)
        output_file.write("\n")

        #
        # Bounds
        #

        output_file.write("bounds \n")

        # Scan all variables even if we're only writing a subset of them.
        # required because we don't store maps by variable type currently.

        # Track the number of integer and binary variables, so you can
        # output their status later.
        niv = nbv = 0

        # FIXME: This is a hack to get nested blocks working...
        lb_string_template = "%"+self._precision_string+" <= "
        ub_string_template = " <= %"+self._precision_string+"\n"
        for block in model.all_blocks(sort_by_keys=True):
            for var_value in active_subcomponents_data_generator(block, Var, sort_by_keys=True):

                if (var_value.fixed and (not output_fixed_variable_bounds)) or (id(var_value) not in self._referenced_variable_ids):
                    continue

                # track the number of integer and binary variables, so we know whether
                # to output the general / binary sections below.
                if isinstance(var_value.domain, IntegerSet):   niv += 1
                elif isinstance(var_value.domain, BooleanSet): nbv += 1

                if var_value.fixed:
                    var_value_lb = var_value.value
                    var_value_ub = var_value.value
                else:
                    var_value_lb = var_value.lb
                    var_value_ub = var_value.ub

                # in the CPLEX LP file format, the default variable
                # bounds are 0 and +inf.  These bounds are in
                # conflict with Pyomo, which assumes -inf and +inf
                # (which we would argue is more rational).
                output_file.write("   ")
                if var_value_lb is not None:
                    output_file.write(lb_string_template % value(var_value_lb))
                else:
                    output_file.write(" -inf <= ")
                name_to_output = object_symbol_dictionary[id(var_value)]
                if name_to_output == "e":
                    msg = 'Attempting to write variable with name' \
                        "'e' in a CPLEX LP formatted file - "    \
                        'will cause a parse failure due to '     \
                        'confusion with numeric values '         \
                        'expressed in scientific notation'
                    raise ValueError(msg)
                output_file.write(name_to_output)
                if var_value.ub is not None:
                    output_file.write(ub_string_template % value(var_value_ub))
                else:
                    output_file.write(" <= +inf\n")

        if niv > 0:

            output_file.write("general\n")

            for block in model.all_blocks(sort_by_keys=True):
                for variable in active_subcomponents_generator(block, Var):
                    for index in sorted(variable.integer_keys()):
                        var_value = variable[index]
                        if (var_value.fixed and (not output_fixed_variable_bounds)) or (id(var_value) not in self._referenced_variable_ids):
                            continue
                        var_name = object_symbol_dictionary[id(var_value)]
                        output_file.write('  %s\n' % var_name)

        if nbv > 0:

            output_file.write("binary\n")

            for block in model.all_blocks(sort_by_keys=True):
                for variable in active_subcomponents_generator(block, Var):
                    for index in sorted(variable.binary_keys()):
                        var_value = variable[index]
                        if (var_value.fixed and (not output_fixed_variable_bounds)) or (id(var_value) not in self._referenced_variable_ids):
                            continue
                        var_name = object_symbol_dictionary[id(var_value)]
                        output_file.write('  %s\n' % var_name)


        # SOS constraints
        #
        # For now, we write out SOS1 and SOS2 constraints in the cplex format
        #
        # All Component objects are stored in model._component, which is a
        # dictionary of {class: {objName: object}}.
        #
        # Consider the variable X,
        #
        #   model.X = Var(...)
        #
        # We print X to CPLEX format as X(i,j,k,...) where i, j, k, ... are the
        # indices of X.
        #
        # TODO: Allow users to specify the variables coefficients for custom
        # branching/set orders - also update ampl.py, CPLEXDirect.py, gurobi_direct.py
        sos1 = solver_capability("sos1")
        sos2 = solver_capability("sos2")
        writtenSOS = False
        for block in model.all_blocks(sort_by_keys=True):
            for soscondata in active_subcomponents_data_generator(block,SOSConstraint):
                level = soscondata.get_level()
                if (level == 1 and not sos1) or (level == 2 and not sos2) or (level > 2):
                    raise Exception(
                        "Solver does not support SOS level %s constraints"
                        % (level,) )
                if writtenSOS == False:
                    output_file.write("SOS\n")
                    writtenSOS = True
                self.printSOS(symbol_map, labeler, soscondata, output_file)

        #
        # wrap-up
        #
        output_file.write("end \n")

        return symbol_map

#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['pyomo2lp', 'pyomo2nl', 'pyomo2osil', 'pyomo2dakota']

import os
import sys
import argparse

from pyutilib.misc import Options, Container

from coopr.opt import ProblemFormat
from coopr.opt.base import SolverFactory
import coopr.pyomo.scripting.util
import coopr.pyomo.scripting.pyomo

from coopr.pyomo.base import Objective, Var, Constraint, \
    active_subcomponents_data_generator


def create_parser(cmd):
    #
    #
    # Setup command-line options
    #
    #
    parser = argparse.ArgumentParser(
                usage = '%s [options] <model_file> [<data_files>]' % cmd
                )
    coopr.pyomo.scripting.pyomo.add_model_group(parser)
    coopr.pyomo.scripting.pyomo.add_logging_group(parser)
    coopr.pyomo.scripting.pyomo.add_misc_group(parser)
    parser.add_argument('model_file', action='store', nargs='?', default='', help='A Python module that defines a Pyomo model')
    parser.add_argument('data_files', action='store', nargs='*', default=[], help='Pyomo data files that defined data used to create a model instance')
    return parser

format = None

def convert(options=Options(), parser=None):
    global format
    if options.save_model is None:
        if format == ProblemFormat.cpxlp:
            options.save_model = 'unknown.lp'
        else:
            options.save_model = 'unknown.'+str(format)
    options.format = format
    #
    data = Options(options=options)
    #
    if options.help_components:
        coopr.pyomo.scripting.util.print_components(data)
        return Container()
    #
    coopr.pyomo.scripting.util.setup_environment(data)
    #
    coopr.pyomo.scripting.util.apply_preprocessing(data, parser=parser)
    if data.error:
        return Container()
    #
    model_data = coopr.pyomo.scripting.util.create_model(data)
    #
    coopr.pyomo.scripting.util.finalize(data, model=model_data.model)
    #
    model_data.options = options
    return model_data


def convert_dakota(options=Options(), parser=None):

    model_file = os.path.basename(options.model_file)
    model_file_no_ext = os.path.splitext(model_file)[0]

    #
    # Set options for writing the .nl and related files
    #

    # By default replace .py with .nl
    if options.save_model is None:
       options.save_model = model_file_no_ext + '.nl'
    options.format = ProblemFormat.nl
    # Dakota requires .row/.col files
    options.symbolic_solver_labels = True

    #
    # Call the core converter
    #
    model_data = convert(options, parser)

    #
    # Generate Dakota input file fragments for the Vars, Objectives, Constraints
    #

    # TODO: the converted model doesn't expose the right symbol_map
    #       for only the vars active in the .nl

    model = model_data.instance

    # Easy way
    #print "VARIABLE:"
    #lines = open(options.save_model.replace('.nl','.col'),'r').readlines()
    #for varName in lines:
    #    varName = varName.strip()
    #    var = model_data.symbol_map.getObject(varName)
    #    print "'%s': %s" % (varName, var)
    #    #print var.pprint()

    # Hard way
    variables = 0
    var_descriptors = []
    var_lb = []
    var_ub = []
    var_initial = []
    tmpDict = model_data.symbol_map.getByObjectDictionary()
    for var in active_subcomponents_data_generator(model, Var):
        if id(var) in tmpDict:
            variables += 1
            var_descriptors.append(var.cname(True))

            # apply user bound, domain bound, or infinite
            if var.lb is not None:
                var_lb.append(str(var.lb))
            elif var.domain.bounds()[0] is not None:
                var_lb.append(str(var.domain.bounds()[0]))
            else:
                var_lb.append("-inf")

            if var.ub is not None:
                var_ub.append(str(var.ub))
            elif var.domain.bounds()[1] is not None:
                var_ub.append(str(var.domain.bounds()[1]))
            else:
                var_ub.append("inf")

            try:
                val = value(var)
            except:
                val = None
            var_initial.append(str(val))

    objectives = 0
    obj_descriptors = []
    for obj in active_subcomponents_data_generator(model, Objective):
        objectives += 1
        obj_descriptors.append(obj.cname(True))

    constraints = 0
    cons_descriptors = []
    cons_lb = []
    cons_ub = []
    for con in active_subcomponents_data_generator(model, Constraint):
        constraints += 1
        cons_descriptors.append(con.cname(True))
        if con.lower is not None:
            cons_lb.append(str(con.lower))
        else:
            cons_lb.append("-inf")
        if con.upper is not None:
            cons_ub.append(str(con.upper))
        else:
            cons_ub.append("inf")

    # Write the Dakota input file fragments

    dakfrag = open(model_file_no_ext + ".dak", 'w')

    dakfrag.write("#--- Dakota variables block ---#\n")
    dakfrag.write("variables\n")
    dakfrag.write("  continuous_design " + str(variables) + '\n')
    dakfrag.write("    descriptors\n")
    for vd in var_descriptors:
        dakfrag.write("      '%s'\n" % vd)
    dakfrag.write("    lower_bounds " + " ".join(var_lb) + '\n')
    dakfrag.write("    upper_bounds " + " ".join(var_ub) + '\n')
    dakfrag.write("    initial_point " + " ".join(var_initial) + '\n')

    dakfrag.write("#--- Dakota interface block ---#\n")
    dakfrag.write("interface\n")
    dakfrag.write("  algebraic_mappings = '" + options.save_model  + "'\n")

    dakfrag.write("#--- Dakota responses block ---#\n")
    dakfrag.write("responses\n")
    dakfrag.write("  objective_functions " + str(objectives) + '\n')

    if (constraints > 0):
        dakfrag.write("  nonlinear_inequality_constraints " + str(constraints) + '\n')
        dakfrag.write("    lower_bounds " + " ".join(cons_lb) + '\n')
        dakfrag.write("    upper_bounds " + " ".join(cons_ub) + '\n')

    dakfrag.write("    descriptors\n")
    for od in obj_descriptors:
        dakfrag.write("      '%s'\n" % od)
    if (constraints > 0):
        for cd in cons_descriptors:
            dakfrag.write("      '%s'\n" % cd)

    # TODO: detect whether gradient information available in model
    dakfrag.write("  analytic_gradients\n")
    dakfrag.write("  no_hessians\n")

    dakfrag.close()

    sys.stdout.write( "Dakota input fragment written to file '%s'\n" 
                      % (model_file_no_ext + ".dak",) )
    return model_data


def pyomo2lp(args=None):
    global format
    parser = create_parser('pyomo2lp')
    format = ProblemFormat.cpxlp
    return coopr.pyomo.scripting.util.run_command(command=convert, parser=parser, args=args, name='pyomo2lp')

def pyomo2lp_main(args=None):
    sys.exit(pyomo2lp(args).errorcode)

def pyomo2nl(args=None):
    global format
    parser = create_parser('pyomo2nl')
    format = ProblemFormat.nl
    return coopr.pyomo.scripting.util.run_command(command=convert, parser=parser, args=args, name='pyomo2nl')

def pyomo2nl_main(args=None):
    sys.exit(pyomo2nl(args).errorcode)

def pyomo2osil(args=None):
    global format
    parser = create_parser('pyomo2osil')
    format = ProblemFormat.osil
    return coopr.pyomo.scripting.util.run_command(command=convert, parser=parser, args=args, name='pyomo2osil')

def pyomo2osil_main(args=None):
    sys.exit(pyomo2osil(args).errorcode)

def pyomo2dakota(args=None):
    global format
    parser = create_parser('pyomo2dakota')
    format = ProblemFormat.nl
    return coopr.pyomo.scripting.util.run_command(command=convert_dakota, parser=parser, args=args, name='pyomo2dakota')

def pyomo2dakota_main(args=None):
    sys.exit(pyomo2dakota(args).errorcode)


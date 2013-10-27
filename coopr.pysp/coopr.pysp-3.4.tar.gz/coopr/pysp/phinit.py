#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2009 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import gc      # garbage collection control.
import os
import pickle  # for serializing
import pstats  # for profiling
import sys
import tempfile
import shutil

from optparse import OptionParser, OptionGroup

# for profiling
try:
    import cProfile as profile
except ImportError:
    import profile

try:
    from pympler.muppy import muppy
    from pympler.muppy import summary
    from pympler.muppy import tracker
    from pympler.asizeof import *
    pympler_available = True
except ImportError:
    pympler_available = False

from pyutilib.component.core import ExtensionPoint
from pyutilib.misc import import_file
from pyutilib.services import TempfileManager
from pyutilib.misc import ArchiveReaderFactory, ArchiveReader

from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
from coopr.pysp.convergence import *
from coopr.pysp.ef import *
from coopr.pysp.ph import *
from coopr.pysp.phutils import reset_nonconverged_variables, reset_stage_cost_variables
from coopr.pysp.scenariotree import *
from coopr.pysp.solutionwriter import ISolutionWriterExtension

#
# The global variable pointing to any temporary unarchiving directory
# created by load_reference_and_scenario_models (or load_models). This is global
# so that scripts like runph, runef, computeconf, and drive_lagrangian can clean
# up after the run
#

_UnarchivingDirectory = None

def cleanup_archives():
    global _UnarchivingDirectory
    if _UnarchivingDirectory is not None:
        shutil.rmtree(_UnarchivingDirectory)
        _UnarchivingDirectory = None

#
# utility method to construct an option parser for ph arguments,
# to be supplied as an argument to the runph method.
#

def construct_ph_options_parser(usage_string):

    solver_list = SolverFactory.services()
    solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
    solver_help = \
    "Specify the solver with which to solve scenario sub-problems.  The "      \
    "following solver types are currently supported: %s; Default: cplex"
    solver_help %= ', '.join( solver_list )

    parser = OptionParser()
    parser.usage = usage_string

    # NOTE: these groups should eventually be queried from the PH, scenario tree, etc. classes (to facilitate re-use).
    inputOpts        = OptionGroup( parser, 'Input Options' )
    scenarioTreeOpts = OptionGroup( parser, 'Scenario Tree Options' )
    phOpts           = OptionGroup( parser, 'PH Options' )
    solverOpts       = OptionGroup( parser, 'Solver Options' )
    postprocessOpts  = OptionGroup( parser, 'Postprocessing Options' )
    outputOpts       = OptionGroup( parser, 'Output Options' )
    otherOpts        = OptionGroup( parser, 'Other Options' )

    parser.add_option_group( inputOpts )
    parser.add_option_group( scenarioTreeOpts )
    parser.add_option_group( phOpts )
    parser.add_option_group( solverOpts )
    parser.add_option_group( postprocessOpts )
    parser.add_option_group( outputOpts )
    parser.add_option_group( otherOpts )

    inputOpts.add_option('-m','--model-directory',
      help='The directory in which all model (reference and scenario) definitions are stored. Default is ".".',
      action="store",
      dest="model_directory",
      type="string",
      default=".")
    inputOpts.add_option('-i','--instance-directory',
      help='The directory in which all instance (reference and scenario) definitions are stored. Default is ".".',
      action="store",
      dest="instance_directory",
      type="string",
      default=".")
    def objective_sense_callback(option, opt_str, value, parser):
        if value in ('min','minimize',minimize):
            parser.values.objective_sense = minimize
        elif value in ('max','maximize',maximize):
            parser.values.objective_sense = maximize
        else:
            parser.values.objective_sense = None
    inputOpts.add_option('-o','--objective-sense-stage-based',
      help='The objective sense to use for the auto-generated scenario instance objective, which is equal to the '
           'sum of the scenario-tree stage costs. Default is None, indicating an Objective has been declared on the '
           'reference model.',
      action="callback",
      dest="objective_sense",
      type="choice",
      choices=[maximize,'max','maximize',minimize,'min','minimize',None],
      default=None,
      callback=objective_sense_callback)
    inputOpts.add_option('--bounds-cfgfile',
      help="The name of a configuration script to set variable bound values. Default is None.",
      action="store",
      dest="bounds_cfgfile",
      default=None)

    scenarioTreeOpts.add_option('--scenario-tree-seed',
      help="The random seed associated with manipulation operations on the scenario tree (e.g., down-sampling or bundle creation). Default is 0, indicating unassigned.",
      action="store",
      dest="scenario_tree_random_seed",
      type="int",
      default=0)
    scenarioTreeOpts.add_option('--scenario-tree-downsample-fraction',
      help="The proportion of the scenarios in the scenario tree that are actually used. Specific scenarios are selected at random. Default is 1.0, indicating no down-sampling.",
      action="store",
      dest="scenario_tree_downsample_fraction",
      type="float",
      default=1.0)
    scenarioTreeOpts.add_option('--scenario-bundle-specification',
      help="The name of the scenario bundling specification to be used when executing Progressive Hedging. Default is None, indicating no bundling is employed. If the specified name ends with a .dat suffix, the argument is interpreted as a filename. Otherwise, the name is interpreted as a file in the instance directory, constructed by adding the .dat suffix automatically",
      action="store",
      dest="scenario_bundle_specification",
      default=None)
    scenarioTreeOpts.add_option('--create-random-bundles',
      help="Specification to create the indicated number of random, equally-sized (to the degree possible) scenario bundles. Default is 0, indicating disabled.",
      action="store",
      dest="create_random_bundles",
      type="int",
      default=None)    

    phOpts.add_option('-r','--default-rho',
      help="The default (global) rho for all blended variables. Default is 1.",
      action="store",
      dest="default_rho",
      type="float",
      default=1.0)
    phOpts.add_option("--overrelax",
      help="Compute weight updates using combination of previous and current variable averages",
      action="store_true",
      dest="overrelax",
      default=False)
    phOpts.add_option("--nu",
      action="store",
      dest="nu",
      type="float",
      default=1.5)      
    phOpts.add_option("--async",
      help="Run PH in asychronous mode after iteration 0. Default is False.",
      action="store_true",
      dest="async",
      default=False)
    phOpts.add_option("--async-buffer-len",
      help="Number of scenarios to collect, if in async mode, before doing statistics and weight updates. Default is 1.",
      action="store",
      dest="async_buffer_len",
      type = "int",
      default=1)
    phOpts.add_option('--rho-cfgfile',
      help="The name of a configuration script to compute PH rho values. Default is None.",
      action="store",
      dest="rho_cfgfile",
      type="string",
      default=None)
    phOpts.add_option('--max-iterations',
      help="The maximal number of PH iterations. Default is 100.",
      action="store",
      dest="max_iterations",
      type="int",
      default=100)
    phOpts.add_option('--termdiff-threshold',
      help="The convergence threshold used in the term-diff and normalized term-diff convergence criteria. Default is 0.0001.",
      action="store",
      dest="termdiff_threshold",
      type="float",
      default=0.0001)
    phOpts.add_option('--enable-free-discrete-count-convergence',
      help="Terminate PH based on the free discrete variable count convergence metric. Default is False.",
      action="store_true",
      dest="enable_free_discrete_count_convergence",
      default=False)
    phOpts.add_option('--enable-normalized-termdiff-convergence',
      help="Terminate PH based on the normalized termdiff convergence metric. Default is True.",
      action="store_true",
      dest="enable_normalized_termdiff_convergence",
      default=True)
    phOpts.add_option('--enable-termdiff-convergence',
      help="Terminate PH based on the termdiff convergence metric. Default is False.",
      action="store_true",
      dest="enable_termdiff_convergence",
      default=False)
    phOpts.add_option('--free-discrete-count-threshold',
      help="The convergence threshold used in the criterion based on when the free discrete variable count convergence criterion. Default is 20.",
      action="store",
      dest="free_discrete_count_threshold",
      type="float",
      default=20)
    phOpts.add_option('--linearize-nonbinary-penalty-terms',
      help="Approximate the PH quadratic term for non-binary variables with a piece-wise linear function, using the supplied number of equal-length pieces from each bound to the average",
      action="store",
      dest="linearize_nonbinary_penalty_terms",
      type="int",
      default=0)
    phOpts.add_option('--breakpoint-strategy',
      help="Specify the strategy to distribute breakpoints on the [lb, ub] interval of each variable when linearizing. 0 indicates uniform distribution. 1 indicates breakpoints at the node min and max, uniformly in-between. 2 indicates more aggressive concentration of breakpoints near the observed node min/max.",
      action="store",
      dest="breakpoint_strategy",
      type="int",
      default=0)
    phOpts.add_option('--retain-quadratic-binary-terms',
      help="Do not linearize PH objective terms involving binary decision variables",
      action="store_true",
      dest="retain_quadratic_binary_terms",
      default=False)
    phOpts.add_option('--drop-proximal-terms',
      help="Eliminate proximal terms (i.e., the quadratic penalty terms) from the weighted PH objective. Default is False.",
      action="store_true",
      dest="drop_proximal_terms",
      default=False)
    phOpts.add_option('--enable-ww-extensions',
      help="Enable the Watson-Woodruff PH extensions plugin. Default is False.",
      action="store_true",
      dest="enable_ww_extensions",
      default=False)
    phOpts.add_option('--ww-extension-cfgfile',
      help="The name of a configuration file for the Watson-Woodruff PH extensions plugin.",
      action="store",
      dest="ww_extension_cfgfile",
      type="string",
      default="")
    phOpts.add_option('--ww-extension-suffixfile',
      help="The name of a variable suffix file for the Watson-Woodruff PH extensions plugin.",
      action="store",
      dest="ww_extension_suffixfile",
      type="string",
      default="")
    phOpts.add_option('--ww-extension-annotationfile',
      help="The name of a variable annotation file for the Watson-Woodruff PH extensions plugin.",
      action="store",
      dest="ww_extension_annotationfile",
      type="string",
      default="")
    phOpts.add_option('--user-defined-extension',
      help="The name of a python module specifying a user-defined PH extension plugin.",
      action="append",
      dest="user_defined_extensions",
      type="string",
      default=[])
    phOpts.add_option("--flatten-expressions", "--linearize-expressions",
      help="EXPERIMENTAL: An option intended for use on linear or mixed-integer models " \
           "in which expression trees in a model (constraints or objectives) are compacted " \
           "into a more memory-efficient and concise form. The trees themselves are eliminated. ",
      action="store_true",
      dest="linearize_expressions",
      default=False)
    phOpts.add_option('--preprocess-fixed-variables',
      help="Preprocess scenario instances if any variables are fixed or freed. The alternative is to simply output the variables with associated bounds. Default is True.",
      action="store_true",
      dest="preprocess_fixed_variables",
      default=True) # presently a no-op

    solverOpts.add_option('--scenario-mipgap',
      help="Specifies the mipgap for all PH scenario sub-problems",
      action="store",
      dest="scenario_mipgap",
      type="float",
      default=None)
    solverOpts.add_option('--scenario-solver-options',
      help="Solver options for all PH scenario sub-problems",
      action="append",
      dest="scenario_solver_options",
      type="string",
      default=[])
    solverOpts.add_option('--solver',
      help=solver_help,
      action="store",
      dest="solver_type",
      type="string",
      default="cplex")
    solverOpts.add_option('--solver-io',
      help='The type of IO used to execute the solver.  Different solvers support different types of IO, but the following are common options: lp - generate LP files, nl - generate NL files, python - direct Python interface, os - generate OSiL XML files.',
      action='store',
      dest='solver_io',
      default=None)    
    solverOpts.add_option('--solver-manager',
      help="The type of solver manager used to coordinate scenario sub-problem solves. Default is serial.",
      action="store",
      dest="solver_manager_type",
      type="string",
      default="serial")
    solverOpts.add_option('--handshake-with-phpyro',
      help="When updating weights, xbars, and rhos across the PHPyro solver manager, it is often expedient to ignore the simple acknowledgement results returned by PH solver servers. Enabling this option instead enables hand-shaking, to ensure message receipt. Clearly only makes sense if the PHPyro solver manager is selected",
      action="store_true",
      dest="handshake_with_phpyro",
      default=False)
    solverOpts.add_option('--disable-warmstarts',
      help="Disable warm-start of scenario sub-problem solves in PH iterations >= 1. Default is False.",
      action="store_true",
      dest="disable_warmstarts",
      default=False)
    solverOpts.add_option('--shutdown-pyro',
      help="Shut down all Pyro-related components associated with the Pyro and PH Pyro solver managers (if specified), including the dispatch server, name server, and any solver servers. Default is False.",
      action="store_true",
      dest="shutdown_pyro",
      default=False)

    postprocessOpts.add_option('--ef-output-file',
      help="The name of the extensive form output file (currently only LP and NL formats are supported), if writing of the extensive form is enabled. Default is efout.lp.",
      action="store",
      dest="ef_output_file",
      type="string",
      default="efout.lp")
    postprocessOpts.add_option('--solve-ef',
      help="Following write of the extensive form model, solve it.",
      action="store_true",
      dest="solve_ef",
      default=False)
    postprocessOpts.add_option('--ef-solver-manager',
      help="The type of solver manager used to execute the extensive form solve. Default is serial.",
      action="store",
      dest="ef_solver_manager_type",
      type="string",
      default="serial")
    postprocessOpts.add_option('--ef-mipgap',
      help="Specifies the mipgap for the EF solve",
      action="store",
      dest="ef_mipgap",
      type="float",
      default=None)
    postprocessOpts.add_option('--disable-ef-warmstart',
      help="Disable warm-start of the post-PH extensive form solve. Default is False.",
      action="store_true",
      dest="disable_ef_warmstart",
      default=False)
    postprocessOpts.add_option('--ef-solver-options',
      help="Solver options for the extensive form problem",
      action="append",
      dest="ef_solver_options",
      type="string",
      default=[])
    postprocessOpts.add_option('--output-ef-solver-log',
      help="Output solver log during the extensive form solve",
      action="store_true",
      dest="output_ef_solver_log",
      default=False)

    outputOpts.add_option('--output-scenario-tree-solution',
      help="Report the full solution (even leaves) in scenario tree format upon termination. Values represent averages, so convergence is not an issue. Default is False.",
      action="store_true",
      dest="output_scenario_tree_solution",
      default=False)
    outputOpts.add_option('--output-solver-logs',
      help="Output solver logs during scenario sub-problem solves",
      action="store_true",
      dest="output_solver_logs",
      default=False)
    outputOpts.add_option('--symbolic-solver-labels',
      help='When interfacing with the solver, use symbol names derived from the model. For example, \"my_special_variable[1_2_3]\" instead of \"v1\". Useful for debugging. When using the ASL interface (--solver-io=nl), generates corresponding .row (constraints) and .col (variables) files. The ordering in these files provides a mapping from ASL index to symbolic model names.',
      action='store_true',
      dest='symbolic_solver_labels',
      default=False)
    outputOpts.add_option('--output-solver-results',
      help="Output solutions obtained after each scenario sub-problem solve",
      action="store_true",
      dest="output_solver_results",
      default=False)
    outputOpts.add_option('--output-times',
      help="Output timing statistics for various PH components",
      action="store_true",
      dest="output_times",
      default=False)
    outputOpts.add_option('--output-instance-construction-times',
      help="Output timing statistics for instance construction timing statistics (client-side only when using PHPyro",
      action="store_true",
      dest="output_instance_construction_times",
      default=False)
    outputOpts.add_option('--report-only-statistics',
      help="When reporting solutions (if enabled), only output per-variable statistics - not the individual scenario values. Default is False.",
      action="store_true",
      dest="report_only_statistics",
      default=False)
    outputOpts.add_option('--report-solutions',
      help="Always report PH solutions after each iteration. Enabled if --verbose is enabled. Default is False.",
      action="store_true",
      dest="report_solutions",
      default=False)
    outputOpts.add_option('--report-weights',
      help="Always report PH weights prior to each iteration. Enabled if --verbose is enabled. Default is False.",
      action="store_true",
      dest="report_weights",
      default=False)
    outputOpts.add_option('--report-for-zero-variable-values',
      help="Report statistics (variables and weights) for all variables, not just those with values differing from 0. Default is False.",
      action="store_true",
      dest="report_for_zero_variable_values",
      default=False)
    outputOpts.add_option('--report-only-nonconverged-variables',
      help="Report statistics (variables and weights) only for non-converged variables. Default is False.",
      action="store_true",
      dest="report_only_nonconverged_variables",
      default=False)
    outputOpts.add_option('--restore-from-checkpoint',
      help="The name of the checkpoint file from which PH should be initialized. Default is \"\", indicating no checkpoint restoration",
      action="store",
      dest="restore_from_checkpoint",
      type="string",
      default="")
    outputOpts.add_option('--solution-writer',
      help="The plugin invoked to write the scenario tree solution. Defaults to the empty list.",
      action="append",
      dest="solution_writer",
      type="string",
      default = [])
    outputOpts.add_option('--suppress-continuous-variable-output',
      help="Eliminate PH-related output involving continuous variables.",
      action="store_true",
      dest="suppress_continuous_variable_output",
      default=False)
    outputOpts.add_option('--verbose',
      help="Generate verbose output for both initialization and execution. Default is False.",
      action="store_true",
      dest="verbose",
      default=False)
    outputOpts.add_option('--write-ef',
      help="Upon termination, write the extensive form of the model - accounting for all fixed variables.",
      action="store_true",
      dest="write_ef",
      default=False)

    otherOpts.add_option('--disable-gc',
      help="Disable the python garbage collecter. Default is False.",
      action="store_true",
      dest="disable_gc",
      default=False)
    if pympler_available:
        otherOpts.add_option("--profile-memory",
                             help="If Pympler is available (installed), report memory usage statistics for objects created after each PH iteration. A value of 0 indicates disabled. A value of 1 forces summary output after each PH iteration >= 1. Values greater than 2 are currently not supported.",
                             action="store",
                             dest="profile_memory",
                             type=int,
                             default=0)
    otherOpts.add_option('-k','--keep-solver-files',
      help="Retain temporary input and output files for scenario sub-problem solves",
      action="store_true",
      dest="keep_solver_files",
      default=False)
    otherOpts.add_option('--profile',
      help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
      action="store",
      dest="profile",
      type="int",
      default=0)
    otherOpts.add_option('--checkpoint-interval',
      help="The number of iterations between writing of a checkpoint file. Default is 0, indicating never.",
      action="store",
      dest="checkpoint_interval",
      type="int",
      default=0)
    otherOpts.add_option('--traceback',
      help="When an exception is thrown, show the entire call stack. Ignored if profiling is enabled. Default is False.",
      action="store_true",
      dest="traceback",
      default=False)

    return parser

#
# Import the reference model and create the scenario tree instance for PH.
# IMPT: This method should be moved into a more generic module - it has nothing
#       to do with PH, and is used elsewhere (by routines that shouldn't have
#       to know about PH).
#

def load_reference_and_scenario_models(archived_model_directory, archived_instance_directory, scenario_bundle_specification, \
                                       scenario_tree_downsample_fraction, scenario_tree_random_seed, \
                                       create_random_bundles, solver_type, verbose):

    #
    # create and populate the reference model/instance pair.
    #

    global _UnarchivingDirectory

    reference_scenario_model = None
    unarchived_model_directory = None
    model_directory_archive = None

    try:

        # un-archive the model directory if necessary
        archived_model_directory, _, archive_subdir = ArchiveReader.normalize_name(archived_model_directory).partition(',')
        if not ArchiveReader.isDir(archived_model_directory):
            if archive_subdir.strip() == '':
                archive_subdir = None
            model_directory_archive = ArchiveReaderFactory(archived_model_directory, subdir=archive_subdir)
            unarchived_model_directory = _UnarchivingDirectory = tempfile.mkdtemp(prefix='unarchived',dir=os.path.dirname(archived_model_directory))
            print("Model directory unarchiving to: %s" % _UnarchivingDirectory)
            model_directory_archive.extractall(path=_UnarchivingDirectory)
        else:
            # let's not deal with the ArchiveReader pure directory interface to avoid making unnecessary copies / links
            unarchived_model_directory = os.path.join(archived_model_directory, archive_subdir.strip())

    except:
        exception = sys.exc_info()[1]
        print("***ERROR: Failed to locate or unarchive "+archived_model_directory+";\nSource error="+str(exception))
        return None, None, None, None, None

    try:
         
        reference_scenario_model_filename = os.path.join(unarchived_model_directory, "ReferenceModel.py")
        if verbose:
            print("Scenario reference model filename="+reference_scenario_model_filename)
        model_import = import_file(reference_scenario_model_filename)
        if "model" not in dir(model_import):
            print("")
            print("***ERROR: Exiting test driver: No 'model' object created in module "+reference_scenario_model_filename)
            return None, None, None, None, None

        if model_import.model is None:
            print("")
            print("***ERROR: Exiting test driver: 'model' object equals 'None' in module "+reference_scenario_model_filename)
            return None, None, None, None, None

        reference_scenario_model = model_import.model

    except IOError:
        exception = sys.exc_info()[1]
        print("***ERROR: Failed to load scenario reference model from file="+reference_scenario_model_filename+";\nSource error="+str(exception))
        return None, None, None, None, None

    #
    # create and populate the scenario tree model
    #

    from coopr.pysp.util.scenariomodels import scenario_tree_model
    scenario_tree_instance = None
    unarchived_instance_directory = None
    instance_directory_archive = None

    try:

        # un-archive the scenario data if necessary
        archived_instance_directory, _, archive_subdir = ArchiveReader.normalize_name(archived_instance_directory).partition(',')
        if not ArchiveReader.isDir(archived_instance_directory):
            if archive_subdir.strip() == '':
                archive_subdir = None
            instance_directory_archive = ArchiveReaderFactory(archived_instance_directory, subdir=archive_subdir)
            if _UnarchivingDirectory is None:
                unarchived_instance_directory = _UnarchivingDirectory = tempfile.mkdtemp(prefix='unarchived',dir=os.path.dirname(archived_instance_directory))
            else:
                unarchived_instance_directory = _UnarchivingDirectory
            print("Instance directory unarchiving to: %s" % _UnarchivingDirectory)
            instance_directory_archive.extractall(path=_UnarchivingDirectory)
        else:
            # let's not deal with the ArchiveReader pure directory interface to avoid making unnecessary copies / links
            unarchived_instance_directory = os.path.join(archived_instance_directory, archive_subdir.strip())

    except:
        exception = sys.exc_info()[1]
        print("***ERROR: Failed to locate or unarchive "+archived_instance_directory+";\nSource error="+str(exception))
        return None, None, None, None, None

    try:

        scenario_tree_bundle_specification_filename = None # until proven otherwise
        if scenario_bundle_specification is not None:
            # we interpret the scenario bundle specification in one of two ways. if the
            # supplied name is a file, it is used directly. otherwise, it is interpreted
            # as the root of a file with a .dat suffix to be found in the instance directory.
            if os.path.exists(os.path.expanduser(scenario_bundle_specification)):
               scenario_tree_bundle_specification_filename = os.path.expanduser(scenario_bundle_specification)
            else:
                scenario_tree_bundle_specification_filename = os.path.join(unarchived_instance_directory, scenario_bundle_specification+".dat")

        scenario_tree_instance_filename = os.path.join(unarchived_instance_directory, "ScenarioStructure.dat")
        if verbose:
            print("Scenario tree instance filename="+scenario_tree_instance_filename)
            if scenario_bundle_specification is not None:
                print("Scenario tree bundle specification filename="+scenario_tree_bundle_specification_filename)

        if scenario_bundle_specification is None:
            scenario_tree_instance = scenario_tree_model.create(filename=scenario_tree_instance_filename)
        else:
            scenario_tree_instance = scenario_tree_model.clone()
            instance_data = ModelData()
            instance_data.add(scenario_tree_instance_filename)
            instance_data.add(scenario_tree_bundle_specification_filename)
            instance_data.read(model=scenario_tree_instance)
            scenario_tree_instance.load(instance_data)

    except IOError:
        exception = sys.exc_info()[1]
        print("***ERROR: Failed to load scenario tree reference instance data from file="+scenario_tree_instance_filename+";\nSource error="+str(exception))
        return None, None, None, None, None

    #
    # construct the scenario tree
    #
    scenario_tree = ScenarioTree(scenariotreeinstance=scenario_tree_instance)

    #
    # compress/down-sample the scenario tree, if operation is required. and the option exists!
    #
    if (scenario_tree_downsample_fraction is not None) and (scenario_tree_downsample_fraction < 1.0):

        scenario_tree.downsample(scenario_tree_downsample_fraction, scenario_tree_random_seed, verbose)

    #
    # create random bundles, if the user has specified such.
    #
    if (create_random_bundles is not None) and (create_random_bundles > 0):
        if scenario_tree.contains_bundles():
            print("***ERROR: Scenario tree already contains bundles - cannot use option --create-random-bundles to over-ride existing bundles")
            return None, None, None, None, None

        num_scenarios = len(scenario_tree._scenarios)
        if create_random_bundles > num_scenarios:
            print("***ERROR: Cannot create more random bundles than there are scenarios!")
            return None, None, None, None, None

        print("Creating "+str(create_random_bundles)+" random bundles using seed="+str(scenario_tree_random_seed))
        scenario_tree.create_random_bundles(scenario_tree_instance, create_random_bundles, scenario_tree_random_seed)

    return reference_scenario_model, scenario_tree, scenario_tree_instance, unarchived_model_directory, unarchived_instance_directory

#
# Create a PH object from a (pickl) checkpoint. Experimental at the moment.
#
def create_ph_from_checkpoint(options):

    # we need to load the reference model, as pickle doesn't save contents of .py files!
    try:
        reference_model_filename = os.path.expanduser(model_directory)+os.sep+"ReferenceModel.py"
        if options.verbose:
            print("Scenario reference model filename="+reference_model_filename)
        model_import = import_file(reference_model_filename)
        if "model" not in dir(model_import):
            print("***ERROR: Exiting test driver: No 'model' object created in module "+reference_model_filename)
            return

        if model_import.model is None:
            print("***ERROR: Exiting test driver: 'model' object equals 'None' in module "+reference_model_filename)
            return None

        reference_model = model_import.model
    except IOError:
        exception = sys.exc_info()[1]
        print("***ERROR: Failed to load scenario reference model from file="+reference_model_filename+"; Source error="+str(exception))
        return None

    # import the saved state

    try:
        checkpoint_file = open(options.restore_from_checkpoint,"r")
        ph = pickle.load(checkpoint_file)
        checkpoint_file.close()

    except IOError:
        exception = sys.exc_info()[1]
        raise RuntimeError(exception)

    # tell PH to build the right solver manager and solver TBD - AND PLUGINS, BUT LATER

    raise RuntimeError("Checkpoint restoration is not fully supported/tested yet!")

    return ph

#
# Create a PH object from scratch.
#

def create_ph_from_scratch(options, reference_model, scenario_tree, unarchived_model_directory, unarchived_instance_directory, dual=False):

    #
    # print the input tree for validation/information purposes.
    #
    if options.verbose:
        scenario_tree.pprint()

    #
    # validate the tree prior to doing anything serious
    #
    if scenario_tree.validate() is False:
        print("***ERROR: Scenario tree is invalid****")
        return None
    else:
        if options.verbose:
            print("Scenario tree is valid!")

    #
    # if any of the ww extension configuration options are specified without the
    # ww extension itself being enabled, halt and warn the user - this has led
    # to confusion in the past, and will save user support time.
    #
    if len(options.ww_extension_cfgfile) > 0 and options.enable_ww_extensions is False:
        print("***ERROR: A configuration file was specified for the WW extension module, but the WW extensions are not enabled!")
        return None

    if len(options.ww_extension_suffixfile) > 0 and options.enable_ww_extensions is False:
        print("***ERROR: A suffix file was specified for the WW extension module, but the WW extensions are not enabled!")
        return None

    if len(options.ww_extension_annotationfile) > 0 and options.enable_ww_extensions is False:
        print("***ERROR: A annotation file was specified for the WW extension module, but the WW extensions are not enabled!")
        return None

    #
    # if a breakpoint strategy is specified without linearization eanbled, halt and warn the user.
    #
    if (options.breakpoint_strategy > 0) and (options.linearize_nonbinary_penalty_terms == 0):
        print("***ERROR: A breakpoint distribution strategy was specified, but linearization is not enabled!")
        return None

    #
    # disable all plugins up-front. then, enable them on an as-needed basis later in this function. the
    # reason that plugins should be disabled is that they may have been programmatically enabled in
    # a previous run of PH, and we want to start from a clean slate.
    #
    ph_extension_point = ExtensionPoint(IPHExtension)

    for plugin in ph_extension_point:
       plugin.disable()

    #
    # deal with any plugins. ww extension comes first currently, followed by an option user-defined plugin.
    # order only matters if both are specified. 
    #
    if options.enable_ww_extensions:

        from coopr.pysp import wwphextension

        # explicitly enable the WW extension plugin - it may have been previously loaded and/or enabled.
        ph_extension_point = ExtensionPoint(IPHExtension)

        for plugin in ph_extension_point(all=True):
           if isinstance(plugin, coopr.pysp.wwphextension.wwphextension):
              plugin.enable()
              # there is no reset-style method for plugins in general, or the ww ph extension
              # in plugin in particular. if no configuration or suffix filename is specified,
              # set to None so that remnants from the previous use of the plugin aren't picked up.
              if len(options.ww_extension_cfgfile) > 0:
                 plugin._configuration_filename = options.ww_extension_cfgfile
              else:
                 plugin._configuration_filename = None
              if len(options.ww_extension_suffixfile) > 0:
                 plugin._suffix_filename = options.ww_extension_suffixfile
              else:
                 plugin._suffix_filename = None
              if len(options.ww_extension_annotationfile) > 0:
                 plugin._annotation_filename = options.ww_extension_annotationfile
              else:
                 plugin._annotation_filename = None

    if len(options.user_defined_extensions) > 0:
        for this_extension in options.user_defined_extensions:
            print("Trying to import user-defined PH extension module="+this_extension)
            # make sure "." is in the PATH.
            original_path = list(sys.path)
            sys.path.insert(0,'.')
            import_file(this_extension)
            print("Module successfully loaded")
            sys.path[:] = original_path # restore to what it was
    #
    # construct the convergence "computer" class.
    #
    converger = None
    # go with the non-defaults first, and then with the default (normalized term-diff).
    if options.enable_free_discrete_count_convergence:
        if options.verbose:
           print("Enabling convergence based on a fixed number of discrete variables")
        converger = NumFixedDiscreteVarConvergence(convergence_threshold=options.free_discrete_count_threshold)
    elif options.enable_termdiff_convergence:
        if options.verbose:
           print("Enabling convergence based on non-normalized term diff criterion")
        converger = TermDiffConvergence(convergence_threshold=options.termdiff_threshold)
    else:
        converger = NormalizedTermDiffConvergence(convergence_threshold=options.termdiff_threshold)

    if pympler_available:
        profile_memory = options.profile_memory
    else:
        profile_memory = 0


    #
    # construct and initialize PH
    #
    if dual is True:
        ph = ProgressiveHedging(options, dual_ph=True)
    else:
        ph = ProgressiveHedging(options, dual_ph=False)

    ph.initialize(model_directory_name=unarchived_model_directory,
                  instance_directory_name=unarchived_instance_directory,
                  model=reference_model, 
                  scenario_tree=scenario_tree, 
                  converger=converger, 
                  linearize=options.linearize_expressions,
                  retain_constraints=options.solve_ef)

    if options.suppress_continuous_variable_output:
        ph._output_continuous_variable_stats = False # clutters up the screen, when we really only care about the binaries.

    return ph

#
# Given a PH object, execute it and optionally solve the EF at the end.
#

def run_ph(options, ph):

    #
    # at this point, we have an initialized PH object by some means.
    #
    start_time = time.time()

    #
    # kick off the solve
    #
    retval = ph.solve()
    if retval is not None:
        raise RuntimeError("No solution was obtained for scenario: "+retval)

    end_ph_time = time.time()

    print("")
    print("Total PH execution time=%.2f seconds" %(end_ph_time - start_time))
    print("")
    if options.output_times:
        ph.print_time_stats()

    solution_writer_plugins = ExtensionPoint(ISolutionWriterExtension)
    for plugin in solution_writer_plugins:
        plugin.write(ph._scenario_tree, ph._instances, "ph")

    # store the binding instance, if created, in order to load
    # the solution back into the scenario tree.
    binding_instance = None

    #
    # create the extensive form binding instance, so that we can either write or solve it (if specified).
    #
    if (options.write_ef) or (options.solve_ef):
        print("Creating extensive form for remainder problem")
        ef_instance_start_time = time.time()
        skip_canonical_repn = False
        if ph._solver.problem_format == ProblemFormat.nl:
            skip_canonical_repn = True
        binding_instance = create_ef_instance(ph._scenario_tree, 
                                              ph._instances, 
                                              skip_canonical_repn=skip_canonical_repn)
        ef_instance_end_time = time.time()
        print("Time to construct extensive form instance=%.2f seconds" %(ef_instance_end_time - ef_instance_start_time))

    #
    # solve the extensive form and load the solution back into the PH scenario tree.
    # contents from the PH solve will obviously be over-written!
    #
    if options.write_ef:

       output_filename = os.path.expanduser(options.ef_output_file)
       # technically, we don't need the symbol map since we aren't solving it.
       print("Starting to write the extensive form")
       ef_write_start_time = time.time()
       symbol_map = write_ef(binding_instance, 
                             ph._instances, 
                             output_filename, 
                             symbolic_solver_labels=options.symbolic_solver_labels,
                             output_fixed_variable_bounds=(not options.preprocess_fixed_variables))
       ef_write_end_time = time.time()
       print("Extensive form written to file="+output_filename)
       print("Time to write output file=%.2f seconds" %(ef_write_end_time - ef_write_start_time))

    if options.solve_ef:

        # set the value of each non-converged, non-final-stage variable to None - 
        # this will avoid infeasible warm-stats.
        reset_nonconverged_variables(ph._scenario_tree, ph._instances)
        reset_stage_cost_variables(ph._scenario_tree, ph._instances)

        # create the solver plugin.
        ef_solver = ph._solver
        if ef_solver is None:
            raise ValueError("Failed to create solver of type="+options.solver_type+" for use in extensive form solve")
        if options.keep_solver_files:
           ef_solver.keepfiles = True
        if len(options.ef_solver_options) > 0:
            print("Initializing ef solver with options="+str(options.ef_solver_options))
            ef_solver.set_options("".join(options.ef_solver_options))
        if options.ef_mipgap is not None:
            if (options.ef_mipgap < 0.0) or (options.ef_mipgap > 1.0):
                raise ValueError("Value of the mipgap parameter for the EF solve must be on the unit interval; value specified=" + str(options.ef_mipgap))
            ef_solver.options.mipgap = float(options.ef_mipgap)

        # create the solver manager plugin.
        ef_solver_manager = SolverManagerFactory(options.ef_solver_manager_type)
        if ef_solver_manager is None:
            raise ValueError("Failed to create solver manager of type="+options.solver_type+" for use in extensive form solve")
        elif isinstance(ef_solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro):
            raise ValueError("Cannot solve an extensive form with solver manager type=phpyro")

        print("Queuing extensive form solve")
        ef_solve_start_time = time.time()
        if (options.disable_ef_warmstart) or (ef_solver.warm_start_capable() is False):        
           ef_action_handle = ef_solver_manager.queue(binding_instance, opt=ef_solver, tee=options.output_ef_solver_log)
        else:
           ef_action_handle = ef_solver_manager.queue(binding_instance, opt=ef_solver, tee=options.output_ef_solver_log, warmstart=True)            
        print("Waiting for extensive form solve")
        ef_results = ef_solver_manager.wait_for(ef_action_handle)

        # a temporary hack - if results come back from Pyro, they
        # won't have a symbol map attached. so create one.
        if ef_results._symbol_map is None:
           ef_results._symbol_map = symbol_map_from_instance(binding_instance)

        # verify that we actually received a solution - if we didn't,
        # then warn and bail.
        if len(ef_results.solution) == 0:
            print("Extensive form solve failed - no solution was obtained")
            return

        print("Done with extensive form solve - loading results")
        binding_instance.load(ef_results)

        print("Storing solution in scenario tree")
        ph._scenario_tree.snapshotSolutionFromInstances()

        ef_solve_end_time = time.time()
        print("Time to solve and load results for the extensive form=%.2f seconds" %(ef_solve_end_time - ef_solve_start_time))

        # print *the* metric of interest.
        print("")
        root_node = ph._scenario_tree._stages[0]._tree_nodes[0]              
        print("***********************************************************************************************")
        print(">>>THE EXPECTED SUM OF THE STAGE COST VARIABLES="+str(root_node.computeExpectedNodeCost())+"<<<")
        print("***********************************************************************************************")

        print("")
        print("Extensive form solution:")
        ph._scenario_tree.pprintSolution()
        print("")
        print("Extensive form costs:")
        ph._scenario_tree.pprintCosts(ph._instances)

        solution_writer_plugins = ExtensionPoint(ISolutionWriterExtension)
        for plugin in solution_writer_plugins:
            plugin.write(ph._scenario_tree, ph._instances, "postphef") 

#
# A simple interface so computeconf, lagrange and etc. can call load_reference_and_scenario_models
# without all the arguments culled from options.
#
def load_models(options):
    # just provides a smaller interface for outside callers
    reference_model, scenario_tree, scenario_tree_instance, unarchived_model_directory, unarchived_instance_directory \
        = load_reference_and_scenario_models(options.model_directory,
                                             options.instance_directory,
                                             options.scenario_bundle_specification,
                                             options.scenario_tree_downsample_fraction,
                                             options.scenario_tree_random_seed,
                                             options.create_random_bundles,
                                             options.solver_type,
                                             options.verbose)
    return reference_model, scenario_tree, scenario_tree_instance, unarchived_model_directory, unarchived_instance_directory


#
# The main PH initialization / runner routine. Really only branches based on
# the construction source - a checkpoint or from scratch.
#

def exec_ph(options,dual=False):

    start_time = time.time()    

    ph = None

    # validate the solution writer plugin exists, to avoid a lot of wasted work.
    for solution_writer_name in options.solution_writer:
        print("Trying to import solution writer="+solution_writer_name)
        pyutilib.misc.import_file(solution_writer_name)
        print("Module successfully loaded")

    # if we are restoring from a checkpoint file, do so - otherwise, construct PH from scratch.
    if len(options.restore_from_checkpoint) > 0:
        ph = create_ph_from_checkpoint(options)

    else:
        reference_model, scenario_tree, scenario_tree_instance, unarchived_model_directory, unarchived_instance_directory  = load_models(options)
        if reference_model is None or scenario_tree is None:
            return
        ph = create_ph_from_scratch(options, reference_model, scenario_tree, unarchived_model_directory, unarchived_instance_directory, dual=dual)

    if ph is None:
        print("***FAILED TO CREATE PH OBJECT")
        return

    run_ph(options, ph)

    if (isinstance(ph._solver_manager, coopr.plugins.smanager.pyro.SolverManager_Pyro) or \
        isinstance(ph._solver_manager, coopr.plugins.smanager.phpyro.SolverManager_PHPyro)) and \
        (options.shutdown_pyro):
        print("Shutting down Pyro solver components")
        shutDownPyroComponents()

    end_time = time.time()            

    print("")
    print("Total execution time=%.2f seconds" %(end_time - start_time))

#
# the main driver routine for the runph script.
#

def main(args=None,dual=False):

    #
    # Top-level command that executes the extensive form writer.
    # This is segregated from run_ef_writer to enable profiling.
    #

    #
    # Parse command-line options.
    #
    try:
        ph_options_parser = construct_ph_options_parser("runph [options]")
        (options, args) = ph_options_parser.parse_args(args=args)
    except SystemExit:
        # the parser throws a system exit if "-h" is specified - catch
        # it to exit gracefully.
        return
    #
    # Control the garbage collector - more critical than I would like at the moment.
    #

    if options.disable_gc:
        gc.disable()
    else:
        gc.enable()

    #
    # Run PH - precise invocation depends on whether we want profiling output.
    #

    # if an exception is triggered and traceback is enabled, 'ans' won't
    # have a value and the return statement from this function will flag
    # an error, masking the stack trace that you really want to see.
    ans = None

    if options.profile > 0:
        #
        # Call the main PH routine with profiling.
        #
        tfile = TempfileManager.create_tempfile(suffix=".profile")
        tmp = profile.runctx('exec_ph(options)',globals(),locals(),tfile)
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cumulative')
        p = p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('cumulative','calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        TempfileManager.clear_tempfiles()
        ans = [tmp, None]
    else:
        #
        # Call the main PH routine without profiling.
        #

        if options.traceback:
            ans = exec_ph(options,dual=dual)
        else:
            try:
                try:
                    ans = exec_ph(options,dual=dual)
                except ValueError:
                    str = sys.exc_info()[1]
                    print("VALUE ERROR:")
                    print(str)
                    raise
                except KeyError:
                    str = sys.exc_info()[1]
                    print("KEY ERROR:")
                    print(str)
                    raise
                except TypeError:
                    str = sys.exc_info()[1]
                    print("TYPE ERROR:")
                    print(str)
                    raise
                except NameError:
                    str = sys.exc_info()[1]
                    print("NAME ERROR:")
                    print(str)
                    raise
                except IOError:
                    str = sys.exc_info()[1]
                    print("IO ERROR:")
                    print(str)
                    raise
                except pyutilib.common.ApplicationError:
                    str = sys.exc_info()[1]
                    print("APPLICATION ERROR:")
                    print(str)
                    raise
                except RuntimeError:
                    str = sys.exc_info()[1]
                    print("RUN-TIME ERROR:")
                    print(str)
                    raise
                except:
                    print("Encountered unhandled exception")
                    traceback.print_exc()
                    raise
            except:
                print("\n")
                print("To obtain further information regarding the source of the exception, use the --traceback option")

                # if an exception is triggered, and we're running with pyro, shut down everything - 
                # not doing so is annoying, and leads to a lot of wasted compute time. but don't 
                # do this if the shutdown-pyro option is disabled => the user wanted 
                if ((options.solver_manager_type == "pyro") or (options.solver_manager_type == "phpyro")) and \
                        (options.shutdown_pyro == True):
                    print("\n")
                    print("Shutting down Pyro solver components, following exception trigger")
                    shutDownPyroComponents()

    # delete temporary unarchived directories
    cleanup_archives()
    
    gc.enable()

    return ans

def PH_main(args=None):
    return main(args=args,dual=False)

def DualPH_main(args=None):
    return main(args=args,dual=True)

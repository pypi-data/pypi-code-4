#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import gc         # garbage collection control.
import os
import pickle
import pstats     # for profiling
import sys
import time
import traceback

from optparse import OptionParser
import itertools
from six import iterkeys, itervalues, iteritems, advance_iterator
from six.moves import zip

try:
    import cProfile as profile
except ImportError:
    import profile

from coopr.opt.base import SolverFactory
from coopr.pysp.scenariotree import *

from pyutilib.misc import import_file, PauseGC
from pyutilib.services import TempfileManager

import Pyro.core
import Pyro.naming
from Pyro.errors import PyroError, NamingError

from coopr.pysp.phinit import *
from coopr.pysp.phutils import *
from coopr.pysp.phobjective import *
from coopr.pysp.ph import _PHBase
from coopr.pyomo.base.expr import identify_variables
from coopr.pysp.phsolverserverutils import _PHServerConfig
from coopr.pysp.phextension import IPHSolverServerExtension

import pyutilib.pyro

class PHSolverServer(pyutilib.pyro.TaskWorker, _PHBase):

    def __init__(self, **kwds):

        pyutilib.pyro.TaskWorker.__init__(self)
        _PHBase.__init__(self)
        
        self._first_solve = True

        # Maps ScenarioTreeID's on the master node ScenarioTree to ScenarioTreeID's on this
        # PHSolverServers's ScenarioTree
        self._master_scenario_tree_id_map = {}

        # the TaskWorker base uses the "type" option to determine the name
        # of the queue from which to request work, via the dispatch server.
        # 
        # the default type is "initialize", which is the queue to which the
        # runph client will transmit initialization to. once initialized,
        # the queue name will be changed to the scenario/bundle name for
        # which this solver server is responsible.
        self.type = "initialize"

        # global handle to ph extension plugins
        self._ph_plugins = ExtensionPoint(IPHSolverServerExtension)

    #
    # Extract the value of all instance variables into a list 
    # of (InstanceID, value) tuples.
    #
    
    def _extract_variable_values(self, scenario, extract=PHSolverServerConfigDefault):
        
        results = {}
        scenario_instance = scenario._instance
        scenariotree_sm_bySymbol = scenario_instance._ScenarioTreeSymbolMap.bySymbol

        var_phinst_sm_byObject = scenario_instance._PHInstanceSymbolMaps[Var].byObject
        var_phinst_sm_bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol

        if extract.TransmitAllVars() is True:
            
            results_Var = []
            if extract.TransmitFixedVars() is True:
                results_Var.extend((instance_id, vardata.value) \
                                    for instance_id, vardata in iteritems(var_phinst_sm_bySymbol))
            else:
                results_Var.extend((instance_id, vardata.value) \
                                    for instance_id, vardata in iteritems(var_phinst_sm_bySymbol) if vardata.fixed is False)
        
        elif extract.TransmitPHVars() is True:
            
            results_Var = []

            full_node_list = scenario._node_list
            nonleaf_node_list = scenario._node_list[:-1]
            node_list = full_node_list if (extract.TransmitPHLeafVars() is True) else nonleaf_node_list

            # ScenarioTree Blended Variables
            for tree_node in node_list:
                vardatas = (scenariotree_sm_bySymbol[variable_id] for variable_id in tree_node._standard_variable_ids)
                if extract.TransmitFixedVars() is True:
                    results_Var.extend((var_phinst_sm_byObject[id(vardata)], vardata.value) for vardata in vardatas)
                else:
                    results_Var.extend((var_phinst_sm_byObject[id(vardata)], vardata.value) for vardata in vardatas if vardata.fixed is False)

            # ScenarioTree Derived Variables
            for tree_node in node_list:
                vardatas = (scenariotree_sm_bySymbol[variable_id] for variable_id in tree_node._derived_variable_ids)
                if extract.TransmitFixedVars() is True:
                    results_Var.extend((var_phinst_sm_byObject[id(vardata)], vardata.value) for vardata in vardatas if (not vardata.is_expression()))
                else:
                    results_Var.extend((var_phinst_sm_byObject[id(vardata)], vardata.value) for vardata in vardatas if (not vardata.is_expression()) and (not vardata.fixed))
                    
            # StageCost Variables (From all stages)
            for tree_node in full_node_list:
                cost_var_name, cost_var_index = tree_node._stage._cost_variable
                cost_var = scenario_instance.find_component(cost_var_name)
                if (cost_var.type() is Var):
                    cost_vardata = cost_var[cost_var_index]
                    results_Var.append((var_phinst_sm_byObject[id(cost_vardata)],cost_vardata.value))
            
            # Transmit linearizing variables so we can evaluate the objective expression
            if self._linearize_nonbinary_penalty_terms > 0:
                for variable_name, variable in iteritems(scenario_instance.active_subcomponents(Var)):
                    if variable_name.startswith("PHQUADPENALTY"):
                        results_Var.extend((var_phinst_sm_byObject[id(vardata)], vardata.value) for vardata in itervalues(variable))
            
            #
            # Extract required variable values to evaluate Expressions on the master node
            #

            # StageCost Expressions (From all stages)
            results_ExpressionVar = set([])
            for tree_node in full_node_list:
                cost_var_name, cost_var_index = tree_node._stage._cost_variable
                cost_var = scenario_instance.find_component(cost_var_name)
                if (cost_var.type() is Expression):
                    cost_exprdata = cost_var[cost_var_index]
                    if extract.TransmitFixedVars() is True:
                        results_ExpressionVar.update((var_phinst_sm_byObject[id(vardata)],vardata.value) for vardata in identify_variables(cost_exprdata))
                    else:
                        results_ExpressionVar.update((var_phinst_sm_byObject[id(vardata)],vardata.value) for vardata in identify_variables(cost_exprdata) if (not vardata.fixed))

            # ScenarioTree Derived Variables (that are Expressions)
            for tree_node in node_list:
                derived_vardatas = (scenariotree_sm_bySymbol[variable_id] for variable_id in tree_node._derived_variable_ids)
                for derivedvardata in derived_vardatas:
                    if derivedvardata.is_expression():
                        if extract.TransmitFixedVars() is True:
                            results_ExpressionVar.update((var_phinst_sm_byObject[id(vardata)],vardata.value) for vardata in identify_variables(derivedvardata))
                        else:
                            results_ExpressionVar.update((var_phinst_sm_byObject[id(vardata)],vardata.value) for vardata in identify_variables(derivedvardata) if (not vardata.fixed))

            if len(results_ExpressionVar) > 0:
                results_Var = tuple(set(results_Var).union(results_ExpressionVar))

        else:
            raise ValueError("Unrecognized PHSolverServer Configuration")

        results[Var] = results_Var

        for key in results:
            results[key] = tuple(results[key])

        return results

    # 
    # Overloading from _PHBase to add a few extra print statements
    #

    def activate_ph_objective_weight_terms(self):

        if self._verbose:
            print("Received request to activate PH objective weight terms for scenario(s)="+str(list(iterkeys(self._instances))))

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        _PHBase.activate_ph_objective_weight_terms(self, transmit=False)

        if self._verbose:
            print("Activating PH objective weight terms")

    # 
    # Overloading from _PHBase to add a few extra print statements
    #

    def deactivate_ph_objective_weight_terms(self):

        if self._verbose:
            print("Received request to deactivate PH objective weight terms for scenario(s)="+str(list(iterkeys(self._instances))))

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        _PHBase.deactivate_ph_objective_weight_terms(self, transmit=False)

        if self._verbose:
            print("Deactivating PH objective weight terms")

    # 
    # Overloading from _PHBase to add a few extra print statements
    #

    def activate_ph_objective_proximal_terms(self):

        if self._verbose:
            print("Received request to activate PH objective proximal terms for scenario(s)="+str(list(iterkeys(self._instances))))

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        _PHBase.activate_ph_objective_proximal_terms(self, transmit=False)

        if self._verbose:
            print("Activating PH objective proximal terms")

    # 
    # Overloading from _PHBase to add a few extra print statements
    #

    def deactivate_ph_objective_proximal_terms(self):

        if self._verbose:
            print("Received request to deactivate PH objective proximal terms for scenario(s)="+str(list(iterkeys(self._instances))))

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        _PHBase.deactivate_ph_objective_proximal_terms(self, transmit=False)

        if self._verbose:
            print("Deactivating PH objective proximal terms")

    def initialize(self,
                   model_directory, 
                   instance_directory, 
                   object_name,
                   objective_sense,
                   solver_type, 
                   solver_io,
                   scenario_bundle_specification,
                   create_random_bundles, 
                   scenario_tree_random_seed,
                   default_rho, 
                   linearize_nonbinary_penalty_terms, 
                   retain_quadratic_binary_terms,
                   drop_proximal_terms,
                   breakpoint_strategy,
                   integer_tolerance,
                   verbose):

        if verbose:
            print("Received request to initialize PH solver server")
            print("")
            print("Model directory: "+model_directory)
            print("Instance directory: "+instance_directory)
            print("Solver type: "+solver_type)
            print("Scenario or bundle name: "+object_name)
            if scenario_bundle_specification != None:
                print("Scenario tree bundle specification: "+scenario_bundle_specification)
            if create_random_bundles != None:
                print("Create random bundles: "+str(create_random_bundles))
            if scenario_tree_random_seed != None:
                print("Scenario tree random seed: "+ str(scenario_tree_random_seed))
            print("Linearize non-binary penalty terms: "+ str(linearize_nonbinary_penalty_terms))

        if self._initialized:
            raise RuntimeError("PH solver servers cannot currently be re-initialized")

        # let plugins know if they care.
        if self._verbose:
            print("Invoking pre-initialization PHSolverServer plugins")
        for plugin in self._ph_plugins:
            plugin.pre_ph_initialization(self)

        self._objective_sense = objective_sense
        self._verbose = verbose
        self._rho = default_rho
        self._linearize_nonbinary_penalty_terms = linearize_nonbinary_penalty_terms
        self._retain_quadratic_binary_terms = retain_quadratic_binary_terms
        self._drop_proximal_terms = drop_proximal_terms
        self._breakpoint_strategy = breakpoint_strategy
        self._integer_tolerance = integer_tolerance

        # the solver instance is persistent, applicable to all instances here.
        self._solver_type = solver_type
        self._solver_io = solver_io
        if self._verbose:
            print("Constructing solver type="+solver_type)
        self._solver = SolverFactory(solver_type,solver_io=self._solver_io)
        if self._solver == None:
            raise ValueError("Unknown solver type=" + solver_type + " specified")

        # we need the base model to construct
        # the scenarios that this server is responsible for.
        # TBD - revisit the various "weird" scenario tree arguments

        # GAH: At this point these should never be any form of compressed archive (unless I messed up the code)
        #      We want to avoid multiple unarchiving of the scenario and model directories. This should
        #      have been done once on the master node before this point, meaning these names should point to the
        #      unarchived directories.
        assert os.path.isdir(model_directory)
        assert os.path.isdir(instance_directory)
        self._model, self._scenario_tree, _, model_directory, instance_directory = load_reference_and_scenario_models(model_directory,
                                                                                                                      instance_directory,
                                                                                                                      scenario_bundle_specification,
                                                                                                                      None,
                                                                                                                      scenario_tree_random_seed,
                                                                                                                      create_random_bundles,
                                                                                                                      solver_type,
                                                                                                                      self._verbose)
          
        if self._model is None or self._scenario_tree is None:
             raise RuntimeError("Unable to launch PH solver server.")

        scenarios_to_construct = []

        if self._scenario_tree.contains_bundles() is True:

            # validate that the bundle actually exists. 
            if self._scenario_tree.contains_bundle(object_name) is False:
                raise RuntimeError("Bundle="+object_name+" does not exist.")
    
            if self._verbose:
                print("Loading scenarios for bundle="+object_name)

            # bundling should use the local or "mini" scenario tree - and 
            # then enable the flag to load all scenarios for this instance.
            scenario_bundle = self._scenario_tree.get_bundle(object_name)
            scenarios_to_construct = scenario_bundle._scenario_names

        else:

            scenarios_to_construct.append(object_name)

        self._problem_states = ProblemStates(scenarios_to_construct)
        
        for scenario_name in scenarios_to_construct:

            print("Creating instance for scenario="+scenario_name)

            if self._scenario_tree.contains_scenario(scenario_name) is False:
                raise RuntimeError("Unable to launch PH solver server - unknown scenario specified with name="+scenario_name+".")

            # create the baseline scenario instance
            scenario_instance = construct_scenario_instance(self._scenario_tree,
                                                            instance_directory,
                                                            scenario_name,
                                                            self._model,
                                                            self._verbose,
                                                            preprocess=False,
                                                            linearize=False)

            self._problem_states.objective_updated[scenario_name] = True
            self._problem_states.user_constraints_updated[scenario_name] = True

            # IMPT: disable canonical representation construction for ASL solvers.
            #       this is a hack, in that we need to address encodings and
            #       the like at a more general level.
            if self._solver.problem_format() == ProblemFormat.nl:
                scenario_instance.skip_canonical_repn = True
                # We will take care of these manually within _preprocess_scenario_instance
                # This will also prevent regenerating the ampl_repn when forming the
                # bundle_ef's
                scenario_instance.gen_obj_ampl_repn = False
                scenario_instance.gen_con_ampl_repn = False

            if scenario_instance is None:
                raise RuntimeError("Unable to launch PH solver server - failed to create instance for scenario="+scenario_name)

            self._instances[scenario_name] = scenario_instance
            self._instances[scenario_name].name = scenario_name
        
        # compact the scenario tree to reflect those instances for which
        # this ph solver server is responsible for constructing. 
        self._scenario_tree.compress(scenarios_to_construct)
        
        # with the scenario instances now available, have the scenario tree 
        # compute the variable match indices at each node.
        self._scenario_tree.linkInInstances(self._instances,
                                            self._objective_sense,
                                            create_variable_ids=True)
        self._objective_sense = minimize if (find_active_objective(self._scenario_tree._scenarios[0]._instance,
                                                      safety_checks=True).is_minimizing()) else maximize

        # let plugins know if they care.
        if self._verbose:
            print("Invoking post-instance-creation PHSolverServer plugins")
        # let plugins know if they care - this callback point allows
        # users to create/modify the original scenario instances and/or
        # the scenario tree prior to creating PH-related parameters,
        # variables, and the like.
        for plugin in self._ph_plugins:
            plugin.post_instance_creation(self)
        
        # augment the instance with PH-specific parameters (weights, rhos, etc).
        # this value and the linearization parameter as a command-line argument.
        self._create_scenario_ph_parameters()

        # create symbol maps for easy storage/transmission of variable values
        symbol_ctypes = (Var, Suffix)
        self._create_instance_symbol_maps(symbol_ctypes)
        
        # form the ph objective weight and proximal expressions
        # Note: The Expression objects for the weight and proximal terms
        #       will be added to the instances objectives but will be assigned values 
        #       of 0.0, so that the original objective function form is maintained.
        #       The purpose is so that we can use this shared Expression object in the bundle
        #       binding instance objectives as well when we call _form_bundle_binding_instances
        #       a few lines down (so regeneration of bundle objective expressions is no longer
        #       required before each iteration k solve.

        self.add_ph_objective_weight_terms()
        # Note: call this function on the base class to avoid the check for whether this
        #       phsolverserver has been initialized
        _PHBase.deactivate_ph_objective_weight_terms(self, transmit=False)
        if drop_proximal_terms is False:
            self.add_ph_objective_proximal_terms()
            # Note: call this function on the base class to avoid the check for whether this
            #       phsolverserver has been initialized
            _PHBase.deactivate_ph_objective_proximal_terms(self, transmit=False)
        
        # create the bundle extensive form, if bundling.
        if self._scenario_tree.contains_bundles() is True:
            self._form_bundle_binding_instances(preprocess_objectives=False)
        
        # preprocess all scenario instances as needed, including top level bundle blocks
        self._preprocess_scenario_instances()
        
        # the TaskWorker base uses the "type" option to determine the name
        # of the queue from which to request work, via the dispatch server.
        self.type = object_name

        for stage in self._scenario_tree._stages[:-1]:

            for tree_node in stage._tree_nodes:

                tree_node._minimums = dict((x,0) for x in tree_node._variable_ids)
                tree_node._maximums = dict((x,0) for x in tree_node._variable_ids)
        

        # let plugins know if they care.
        if self._verbose:
            print("Invoking post-initialization PHSolverServer plugins")
        for plugin in self._ph_plugins:
            plugin.post_ph_initialization(self)

        # we're good to go!
        self._initialized = True

    def collect_results(self, scenario_name, var_config):
        
        ExtractionConfig = _PHServerConfig(var_config)
        if self._scenario_tree.contains_bundles() is True:
            variable_values = {}
            for scenario in self._scenario_tree._scenarios:
                variable_values[scenario._name] = self._extract_variable_values(scenario, ExtractionConfig)
        else:
            variable_values = self._extract_variable_values(self._scenario_tree._scenario_map[scenario_name], ExtractionConfig)

        return variable_values

    def solve(self, 
              object_name, 
              tee,
              keepfiles,
              symbolic_solver_labels,
              preprocess_fixed_variables,
              solver_options, 
              solver_suffixes,
              warmstart,
              cache_results):

      if self._verbose:
          if self._scenario_tree.contains_bundles() is True:
              print("Received request to solve scenario bundle="+object_name)
          else:
              print("Received request to solve scenario instance="+object_name)

      if self._initialized is False:
          raise RuntimeError("PH solver server has not been initialized!")

      self._tee = tee
      self._symbolic_solver_labels = symbolic_solver_labels
      self._preprocess_fixed_variables = preprocess_fixed_variables
      self._solver_options = solver_options
      self._solver_suffixes = solver_suffixes
      self._warmstart = warmstart

      if self._first_solve is True:
          # let plugins know if they care.
          if self._verbose:
              print("Invoking pre-iteration-0-solve PHSolverServer plugins")
          for plugin in self._ph_plugins:
              plugin.pre_iteration_0_solve(self)
      else:
          # let plugins know if they care.
          if self._verbose:
              print("Invoking pre-iteration-k-solve PHSolverServer plugins")
          for plugin in self._ph_plugins:
              plugin.pre_iteration_k_solve(self)

      # process input solver options - they will be persistent across to the  next solve. 
      # TBD: we might want to re-think a reset() of the options, or something.
      for key,value in iteritems(self._solver_options):
          if self._verbose:
              print("Processing solver option="+key+", value="+str(value))
          self._solver.options[key] = value

      # with the introduction of piecewise linearization, the form of the
      # penalty-weighted objective is no longer fixed. thus, when linearizing,
      # we need to construct (or at least modify) the constraints used to
      # compute the linearized cost terms.
      if (self._linearize_nonbinary_penalty_terms > 0):
          # These functions will do nothing if ph proximal terms are not 
          # present on the model
          self.form_ph_linearized_objective_constraints()
          # if linearizing, clear the values of the PHQUADPENALTY* variables.
          # if they have values, this can intefere with warm-starting due to
          # constraint infeasibilities.
          self._reset_instance_linearization_variables()
          
      self._preprocess_scenario_instances()

      if self._first_solve is False:

          # GAH: We may need to redefine our concept of warmstart. These values could
          #      be helpful in the nonlinear case (or could be better than 0.0, the
          #      likely default used by the solver when these initializations are not
          #      placed in the NL file. **Note: Initializations go into the NL file
          #      independent of the "warmstart" keyword

          if self._scenario_tree.contains_bundles() is True:
              # clear non-converged variables and stage cost variables, to ensure feasible warm starts.
              reset_nonconverged_variables(self._scenario_tree, self._instances)
              reset_stage_cost_variables(self._scenario_tree, self._instances)
          else:
              # clear stage cost variables, to ensure feasible warm starts.
              reset_stage_cost_variables(self._scenario_tree, self._instances)
      
      if self._scenario_tree.contains_bundles() is True:

          if self._scenario_tree.contains_bundle(object_name) is False:
              print("Requested scenario bundle to solve not known to PH solver server!")
              return None

          bundle_ef_instance = self._bundle_binding_instance_map[object_name]

          if  (self._warmstart is True) and (self._solver.warm_start_capable() is True):
              results = self._solver.solve(bundle_ef_instance,
                                           tee=self._tee,
                                           keepfiles=keepfiles,
                                           symbolic_solver_labels=self._symbolic_solver_labels,
                                           output_fixed_variable_bounds=(not self._preprocess_fixed_variables),
                                           suffixes=self._solver_suffixes,
                                           warmstart=True)
          else:
              results = self._solver.solve(bundle_ef_instance,
                                           tee=self._tee,
                                           keepfiles=keepfiles,
                                           symbolic_solver_labels=self._symbolic_solver_labels,
                                           output_fixed_variable_bounds=(not self._preprocess_fixed_variables),
                                           suffixes=self._solver_suffixes)

          if self._verbose:
              print("Successfully solved scenario bundle="+object_name)

          if len(results.solution) == 0:
              results.write()
              raise RuntimeError("Solve failed for bundle="+object_name+"; no solutions generated")

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          bundle_ef_instance.load(results)

          if cache_results:
              fixed_results = dict((scenario_name,tuple((instance_id, vardata.value, vardata.stale) \
                                                            for instance_id, vardata in \
                                                            iteritems(scenario_instance._PHInstanceSymbolMaps[Var].bySymbol) if vardata.fixed)) for \
                                       scenario_name, scenario_instance in iteritems(self._bundle_scenario_instance_map[object_name]))
              self._cached_solutions[object_name] = (results, fixed_results)

          if self._verbose:
              print("Successfully loaded solution for bundle="+object_name)

          variable_values = {}
          for scenario in self._scenario_tree._scenarios:
              variable_values[scenario._name] = self._extract_variable_values(scenario)

          suffix_values = {}

          # suffixes are stored on the master block.
          bundle_ef_instance = self._bundle_binding_instance_map[object_name]            

          for scenario in self._scenario_tree._scenarios:
              # NOTE: We are only presently extracting suffix values for constraints, as this whole
              #       interface is experimental. And probably inefficient. But it does work.
              scenario_instance = self._instances[scenario._name]
              this_scenario_suffix_values = {}
              for suffix_name in self._solver_suffixes:
                  this_suffix_map = {}
                  suffix = getattr(bundle_ef_instance, suffix_name)
                  # TODO: This needs to be over all blocks
                  for constraint_name, constraint in iteritems(scenario_instance.active_subcomponents(Constraint)):
                      this_constraint_suffix_map = {}
                      for index, constraint_data in iteritems(constraint):
                          this_constraint_suffix_map[index] = suffix.getValue(constraint_data)
                      this_suffix_map[constraint_name] = this_constraint_suffix_map
                  this_scenario_suffix_values[suffix_name] = this_suffix_map
              suffix_values[scenario._name] = this_scenario_suffix_values

          # auxilliary values are those associated with the solve itself. 
          # presently, we don't extract any auxilliary values for bundles.
          auxilliary_values = {}
                            
      else:

          if object_name not in self._instances:
              print("Requested instance to solve not in PH solver server instance collection!")
              return None

          scenario = self._scenario_tree._scenario_map[object_name]
          scenario_instance = self._instances[object_name]

          if (self._warmstart is True) and (self._solver.warm_start_capable() is True):
             results = self._solver.solve(scenario_instance, 
                                          tee=self._tee, 
                                          warmstart=True, 
                                          keepfiles=keepfiles, 
                                          symbolic_solver_labels=self._symbolic_solver_labels, 
                                          output_fixed_variable_bounds=(not self._preprocess_fixed_variables),
                                          suffixes=self._solver_suffixes) 
          else:
             results = self._solver.solve(scenario_instance, 
                                          tee=self._tee, 
                                          keepfiles=keepfiles, 
                                          symbolic_solver_labels=self._symbolic_solver_labels, 
                                          output_fixed_variable_bounds=(not self._preprocess_fixed_variables),
                                          suffixes=self._solver_suffixes)

          if self._verbose:
              print("Successfully solved scenario instance="+object_name)

          if len(results.solution) == 0:
              results.write()
              raise RuntimeError("Solve failed for scenario="+object_name+"; no solutions generated")

          # load the results into the instances on the server side. this is non-trivial
          # in terms of computation time, for a number of reasons. plus, we don't want
          # to pickle and return results - rather, just variable-value maps.
          scenario_instance.load(results)

          if cache_results:
              fixed_results = tuple((instance_id, vardata.value, vardata.stale) \
                                        for instance_id, vardata in \
                                        iteritems(scenario_instance._PHInstanceSymbolMaps[Var].bySymbol) if vardata.fixed)
              self._cached_solutions[object_name] = (results, fixed_results)

          if self._verbose:
              print("Successfully loaded solution for scenario="+object_name)

          variable_values = self._extract_variable_values(scenario)

          # extract suffixes into a dictionary, mapping suffix names to dictionaries that in
          # turn map constraint names to (index, suffix-value) pairs.
          suffix_values = {}

          # NOTE: We are only presently extracting suffix values for constraints, as this whole
          #       interface is experimental. And probably inefficient. But it does work.
          for suffix_name in self._solver_suffixes:
              this_suffix_map = {}
              suffix = getattr(scenario_instance, suffix_name)
              # TODO: This needs to be over all blocks
              for constraint_name, constraint in iteritems(scenario_instance.active_subcomponents(Constraint)):
                  this_constraint_suffix_map = {}
                  for index, constraint_data in iteritems(constraint):
                      this_constraint_suffix_map[index] = suffix.getValue(constraint_data)
                  this_suffix_map[constraint_name] = this_constraint_suffix_map
              suffix_values[suffix_name] = this_suffix_map

          # auxilliary values are those associated with the solve itself. 
          auxilliary_values = {}

          solution0 = results.solution(0)
          if hasattr(solution0, "gap"):
              auxilliary_values["gap"] = solution0.gap

          auxilliary_values["user_time"] = results.solver.user_time

      solve_method_result = (variable_values, suffix_values, auxilliary_values)

      if self._first_solve is True:
          # let plugins know if they care.
          if self._verbose:
              print("Invoking post-iteration-0-solve PHSolverServer plugins")
          for plugin in self._ph_plugins:
              plugin.post_iteration_0_solve(self)
      else:
          # let plugins know if they care.
          if self._verbose:
              print("Invoking post-iteration-k-solve PHSolverServer plugins")
          for plugin in self._ph_plugins:
              plugin.post_iteration_k_solve(self)

      self._first_solve = False

      return solve_method_result

    def update_master_scenario_tree_ids(self, scenario_name, new_ids):

        scenario_instance = self._instances[scenario_name]

        symbol_map = getattr(scenario_instance,"_MASTERScenarioTreeSymbolMap",None)
        if symbol_map is None:
            symbol_map = scenario_instance._MASTERScenarioTreeSymbolMap = BasicSymbolMap()

        var_phinst_sm_bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol
        symbol_map.updateSymbols([(var_phinst_sm_bySymbol[instance_id],master_scenario_tree_id) \
                                      for instance_id, master_scenario_tree_id in new_ids])

        scenariotree_sm_byObject = scenario_instance._ScenarioTreeSymbolMap.byObject
        self._master_scenario_tree_id_map.update((master_scenario_tree_id, scenariotree_sm_byObject[id(var_phinst_sm_bySymbol[instance_id])]) \
                                      for instance_id, master_scenario_tree_id in new_ids)
    #
    # updating xbars only applies to scenarios - not bundles.
    #
    # TODO: Do something smart with xbars parameter updates since they are shared for bundles
    def update_xbars(self, scenario_name, new_xbars):

        if self._verbose:
            print("Received request to update xbars for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update weights for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        # Flag the preprocessor if necessary
        if self._problem_states.has_ph_objective_proximal_terms[scenario_name]:
            self._problem_states.objective_updated[scenario_name] = True

        # Update the xbar paramter
        master_id_map = self._master_scenario_tree_id_map
        for xbar_parameter_name, xbar_update in iteritems(new_xbars):
            instance_xbar_parameter = scenario_instance.find_component(xbar_parameter_name)
            instance_xbar_parameter.store_values(dict((master_id_map[master_id_index], value) \
                                                       for master_id_index, value in xbar_update))

    #
    # updating weights only applies to scenarios - not bundles.
    #
    def update_weights(self, scenario_name, new_weights):

        if self._verbose:
            print("Received request to update weights and averages for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update weights for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        # Flag the preprocessor if necessary
        if self._problem_states.has_ph_objective_weight_terms[scenario_name]:
            self._problem_states.objective_updated[scenario_name] = True

        # Update the weights parameter
        master_id_map = self._master_scenario_tree_id_map
        for weight_parameter_name, weight_update in iteritems(new_weights):
            instance_weight_parameter = scenario_instance.find_component(weight_parameter_name)
            instance_weight_parameter.store_values(dict((master_id_map[master_id_index], value) \
                                                       for master_id_index, value in weight_update))

    #
    # updating bounds is only applicable to scenarios.
    #
    def update_bounds(self, scenario_name, new_bounds):

        if self._verbose:
            print("Received request to update variable bounds for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update variable bounds for instance not in PH solver server instance collection!")
            return None

        scenario_instance = self._instances[scenario_name]
        var_phinst_sm_bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol

        for instance_id, lower_bound, upper_bound in new_bounds:

            vardata = var_phinst_sm_bySymbol[instance_id]
            vardata.lb = lower_bound
            vardata.ub = upper_bound

    #
    # updating rhos is only applicable to scenarios.
    #
    def update_rhos(self, scenario_name, new_rhos):

        if self._verbose:
            print("Received request to update rhos for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to update rhos for scenario="+scenario_name+", which is not in the PH solver server instance set="+str(self._instances.keys()))
            return None
        scenario_instance = self._instances[scenario_name]

        # Flag the preprocessor if necessary
        if self._problem_states.has_ph_objective_proximal_terms[scenario_name]:
            self._problem_states.objective_updated[scenario_name] = True

        # update the rho parameters
        master_id_map = self._master_scenario_tree_id_map
        for rho_parameter_name, rho_update in iteritems(new_rhos):
            instance_rho_parameter = scenario_instance.find_component(rho_parameter_name)
            instance_rho_parameter.store_values(dict((master_id_map[master_id_index], value) \
                                                       for master_id_index, value in rho_update))

    #
    # updating tree node statistics is bundle versus scenario agnostic.
    #

    def update_tree_node_statistics(self, scenario_name, new_node_minimums, new_node_maximums):

        if self._verbose:
            if self._scenario_tree.contains_bundles() is True:
                print("Received request to update tree node statistics for bundle="+scenario_name)
            else:
                print("Received request to update tree node statistics for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        master_id_map = self._master_scenario_tree_id_map

        for tree_node_name, tree_node_minimums in iteritems(new_node_minimums):

            this_tree_node_minimums = self._scenario_tree._tree_node_map[tree_node_name]._minimums
            this_tree_node_minimums.update((master_id_map[master_id_index], value) \
                                           for master_id_index, value in tree_node_minimums)

        for tree_node_name, tree_node_maximums in iteritems(new_node_maximums):

            this_tree_node_maximums = self._scenario_tree._tree_node_map[tree_node_name]._maximums
            this_tree_node_maximums.update((master_id_map[master_id_index], value) \
                                           for master_id_index, value in tree_node_maximums)

    #
    # define the indicated suffix on my scenario instance. not dealing with bundles right now.
    #

    def define_import_suffix(self, object_name, suffix_name):

        if self._verbose:
            if self._scenario_tree.contains_bundles() is True:
                print("Received request to define import suffix="+suffix_name+" for bundle="+object_name)
            else:
                print("Received request to define import suffix="+suffix_name+" for scenario="+object_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if self._scenario_tree.contains_bundles() is True:

            bundle_ef_instance = self._bundle_binding_instance_map[object_name]
            
            bundle_ef_instance.add_component(suffix_name, Suffix(direction=Suffix.IMPORT))

        else:

            if object_name not in self._instances:
                print("ERROR: Received request to define import suffix="+suffix_name+" for scenario="+object_name+", which is not in the collection of PH solver server instances="+str(self._instances.keys()))
                return None
            scenario_instance = self._instances[object_name]

            scenario_instance.add_component(suffix_name, Suffix(direction=Suffix.IMPORT))

    #
    # invoke the indicated function in the specified module. independent of scenario instance.
    #

    def invoke_external_function(self, scenario_name, module_name, function_name):

        from pyutilib.misc import import_file
        from six import iterkeys

        if self._verbose:
            print("Received request to invoke external function="+function_name+" in module="+module_name+" on scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to invoke external function for instance not in PH solver server instance collection!")
            return None
        scenario_instance = self._instances[scenario_name]

        this_module = import_file(module_name)

        if not hasattr(this_module, function_name):
            raise RuntimeError("Function="+function_name+" is not present in module="+module_name)

        getattr(this_module, function_name)(scenario_instance)

    #
    # restore solutions for all of my scenario instances.
    #

    def restoreCachedScenarioSolutions(self, object_name):

        if self._verbose:
            if self._scenario_tree.contains_bundles() is True:
                print("Received request to restore solutions for bundle="+object_name)
            else:
                print("Received request to restore solutions for scenario="+object_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if self._scenario_tree.contains_bundles() is True:
            # validate that the bundle actually exists. 
            if self._scenario_tree.contains_bundle(object_name) is False:
                raise RuntimeError("Bundle="+object_name+" does not exist.")
        else:
            if object_name not in self._instances:
                raise RuntimeError(object_name+" is not in the PH solver server instance collection")

        if len(self._cached_solutions) is 0:
            raise RuntimeError("Cannot restore scenario solutions - the cached scenario solution map is empty!")

        results, fixed_results = self._cached_solutions[object_name]
        if self._scenario_tree.contains_bundles() is True:
            bundle_ef_instance = self._bundle_binding_instance_map[object_name]
            bundle_ef_instance.load(results)
            for scenario_name, scenario_fixed_results in iteritems(fixed_results):
                scenario_instance = self._instances[scenario_name]
                bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol
                for instance_id, varvalue, stale_flag in scenario_fixed_results:
                    vardata = bySymbol[instance_id]
                    vardata.value = varvalue
                    vardata.fixed = True
                    vardata.stale = stale_flag
        else:
            scenario_instance = self._instances[object_name]
            scenario_instance.load(results)
            bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol
            for instance_id, varvalue, stale_flag in fixed_results:
                vardata = bySymbol[instance_id]
                vardata.value = varvalue
                vardata.fixed = True
                vardata.stale = stale_flag

    #
    # fix variables as instructed by the PH client.
    #
    def fix_variables(self, scenario_name, variables_to_fix):

        if self._verbose:
            print("Received request to fix variables for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to fix variables for instance="+scenario_name+", which is not in the PH solver server instance collection")
            return None
        scenario_instance = self._instances[scenario_name]

        self._problem_states.fixed_variables[scenario_name].extend(variables_to_fix)

        # TODO: inform the tree node _fixed

        for variable_name, index in variables_to_fix:
           if self._verbose is True:
               print("Fixing variable="+variable_name+indexToString(index)+" on instance="+scenario_name)
           scenario_instance.find_component(variable_name)[index].fixed = True

    #
    # free variables as instructed by the PH client.
    #
    def free_variables(self, scenario_name, variables_to_free):

        if self._verbose:
            print("Received request to free variables for scenario="+scenario_name)

        if self._initialized is False:
            raise RuntimeError("PH solver server has not been initialized!")

        if scenario_name not in self._instances:
            print("ERROR: Received request to free variables for instance="+scenario_name+", which is not in the PH solver server instance collection")
            return None
        scenario_instance = self._instances[scenario_name]

        self._problem_states.freed_variables[scenario_name].extend(variables_to_free)

        # TODO: inform the tree node _fixed

        for variable_name, index in variables_to_free:
           if self._verbose is True:
               print("Freeing variable="+variable_name+indexToString(index)+" on instance="+scenario_name)
           # NOTE: If a variable was previously fixed, then by definition it had a valid value.
           #       Thus, whe we free the variable, we assign the value as not stale
           scenario_instance.find_component(variable_name)[index].fixed = False
           scenario_instance.find_component(variable_name)[index].stale = False

    def process(self, data):

        suspend_gc = PauseGC()

        result = None
        if data.action == "initialize":
           result = self.initialize(data.model_directory, 
                                    data.instance_directory, 
                                    data.object_name,
                                    data.objective_sense,
                                    data.solver_type, 
                                    data.solver_io,
                                    data.scenario_bundle_specification,
                                    data.create_random_bundles, 
                                    data.scenario_tree_random_seed,
                                    data.default_rho, 
                                    data.linearize_nonbinary_penalty_terms, 
                                    data.retain_quadratic_binary_terms,
                                    data.drop_proximal_terms,
                                    data.breakpoint_strategy,
                                    data.integer_tolerance,
                                    data.verbose)

        elif data.action == "collect_results":
            result = self.collect_results(data.name, 
                                          data.var_config)
        elif data.action == "solve":
            # we are adding the following code because some solvers, including
            # CPLEX, are not all that robust - in that they can spontaneously
            # and sporadically fail. ultimately, this should be command-line
            # option driver.
            max_num_attempts = 2 
            attempts_so_far = 0
            successful_solve = False
            while (not successful_solve):
                try:
                    attempts_so_far += 1
                    result = self.solve(data.name,
                                        data.tee,
                                        data.keepfiles,
                                        data.symbolic_solver_labels,
                                        data.preprocess_fixed_variables,
                                        data.solver_options, 
                                        data.solver_suffixes,
                                        data.warmstart,
                                        data.cache_results)
                    successful_solve = True
                except pyutilib.common.ApplicationError as exc:
                    print("Solve failed for object=%s - this was attempt=%d" % (data.name, attempts_so_far))
                    if (attempts_so_far == max_num_attempts):
                        print("Aborting PH solver server - the maximum number of solve attempts=%d have been executed" % max_num_attempts)
                        raise exc

            if attempts_so_far > 1:
                print("Successfully recovered from failed solve for object=%s" % data.name)
                    
        elif data.action == "activate_ph_objective_proximal_terms":
            self.activate_ph_objective_proximal_terms()
            result = True

        elif data.action == "deactivate_ph_objective_proximal_terms":
            self.deactivate_ph_objective_proximal_terms()
            result = True

        elif data.action == "activate_ph_objective_weight_terms":
            self.activate_ph_objective_weight_terms()
            result = True

        elif data.action == "deactivate_ph_objective_weight_terms":
            self.deactivate_ph_objective_weight_terms()
            result = True

        elif data.action == "update_scenario_tree_ids":
           if self._scenario_tree.contains_bundles() is True:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_master_scenario_tree_ids(scenario_name, 
                                                        data.new_ids[scenario_name])
           else:
               self.update_master_scenario_tree_ids(data.name, 
                                                    data.new_ids)
           result = True

        elif data.action == "load_bounds":
           if self._scenario_tree.contains_bundles() is True:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_bounds(scenario_name, 
                                      data.new_bounds[scenario_name])
           else:
               self.update_bounds(data.name, 
                                  data.new_bounds)
           result = True           

        elif data.action == "load_rhos":
           if self._scenario_tree.contains_bundles() is True:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_rhos(scenario_name, 
                                    data.new_rhos[scenario_name])
           else:
               self.update_rhos(data.name, 
                                data.new_rhos)
           result = True

        elif data.action == "fix_variables":
           if self._scenario_tree.contains_bundles() is True:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.fix_variables(scenario_name, 
                                      data.fixed_variables[scenario_name])
           else:
               self.fix_variables(data.name, 
                                  data.fixed_variables)
           result = True

        elif data.action == "free_variables":
           if self._scenario_tree.contains_bundles() is True:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.free_variables(scenario_name,
                                       data.freed_variables[scenario_name])
           else:
               self.free_variables(data.name, 
                                   data.freed_variables)
           result = True

        elif data.action == "load_weights":
           if self._scenario_tree.contains_bundles() is True:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_weights(scenario_name, 
                                       data.new_weights[scenario_name])
           else:
               self.update_weights(data.name, 
                                   data.new_weights)
           result = True

        elif data.action == "load_xbars":
           if self._scenario_tree.contains_bundles() is True:
               for scenario_name, scenario_instance in iteritems(self._instances):
                   self.update_xbars(scenario_name, 
                                     data.new_xbars[scenario_name])
           else:
               self.update_xbars(data.name,
                                 data.new_xbars)
           result = True

        elif data.action == "load_tree_node_stats":
           self.update_tree_node_statistics(data.name, 
                                            data.new_mins, 
                                            data.new_maxs)
           result = True

        elif data.action == "define_import_suffix":
            self.define_import_suffix(data.name, 
                                      data.suffix_name)
            result = True

        elif data.action == "invoke_external_function":
           self.invoke_external_function(data.name,
                                         data.module_name,
                                         data.function_name)
           result = True

        elif data.action == "restore_cached_scenario_solutions":
            # don't pass the scenario argument - by default,
            # we restore solutions for all of our instances.
           self.restoreCachedScenarioSolutions(data.name)
           result = True

        else:
           raise RuntimeError("ERROR: Unknown action="+str(data.action)+" received by PH solver server")

        # a bit goofy - the Coopr Pyro infrastructure 
        return pickle.dumps(result)

#
# utility method to construct an option parser for ph arguments, to be
# supplied as an argument to the runph method.
#

def construct_options_parser(usage_string):

    parser = OptionParser()
    parser.add_option("--verbose",
                      help="Generate verbose output for both initialization and execution. Default is False.",
                      action="store_true",
                      dest="verbose",
                      default=False)
    parser.add_option("--profile",
                      help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
                      action="store",
                      dest="profile",
                      type="int",
                      default=0)
    parser.add_option("--disable-gc",
                      help="Disable the python garbage collecter. Default is False.",
                      action="store_true",
                      dest="disable_gc",
                      default=False)
    parser.add_option('--user-defined-extension',
                      help="The name of a python module specifying a user-defined PHSolverServer extension plugin.",
                      action="append",
                      dest="user_defined_extensions",
                      type="string",
                      default=[])

    parser.usage=usage_string

    return parser

#
# Execute the PH solver server daemon.
#

def run_server(options):

    # just spawn the daemon!
    pyutilib.pyro.TaskWorkerServer(PHSolverServer)

def run(args=None):

    #
    # Top-level command that executes the ph solver server daemon.
    # This is segregated from phsolverserver to faciliate profiling.
    #

    #
    # Parse command-line options.
    #
    try:
        options_parser = construct_options_parser("phsolverserver [options]")
        (options, args) = options_parser.parse_args(args=args)
    except SystemExit:
        # the parser throws a system exit if "-h" is specified - catch
        # it to exit gracefully.
        return

    # for a one-pass execution, garbage collection doesn't make
    # much sense - so it is disabled by default. Because: It drops
    # the run-time by a factor of 3-4 on bigger instances.
    if options.disable_gc:
        gc.disable()
    else:
        gc.enable()

    if len(options.user_defined_extensions) > 0:
        for this_extension in options.user_defined_extensions:
            print("Trying to import user-defined PHSolverServer extension module="+this_extension)
            # make sure "." is in the PATH.
            original_path = list(sys.path)
            sys.path.insert(0,'.')
            import_file(this_extension)
            print("Module successfully loaded")
            sys.path[:] = original_path # restore to what it was

    if options.profile > 0:
        #
        # Call the main PH routine with profiling.
        #
        tfile = TempfileManager.create_tempfile(suffix=".profile")
        tmp = profile.runctx('run_server(options)',globals(),locals(),tfile)
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
        ans = run_server(options)

    gc.enable()

    return ans

def main():
    exception_trapped = False
    try:
        run()
    except IOError:
        msg = sys.exc_info()[1]
        print("IO ERROR:")
        print(msg)
        exception_trapped = True
    except pyutilib.common.ApplicationError:
        msg = sys.exc_info()[1]
        print("APPLICATION ERROR:")
        print(str(msg))
        exception_trapped = True
    except RuntimeError:
        msg = sys.exc_info()[1]
        print("RUN-TIME ERROR:")
        print(str(msg))
        exception_trapped = True
    # pyutilib.pyro tends to throw SystemExit exceptions if things cannot be found or hooked
    # up in the appropriate fashion. the name is a bit odd, but we have other issues to worry 
    # about. we are dumping the trace in case this does happen, so we can figure out precisely
    # who is at fault.
    except SystemExit:
        msg = sys.exc_info()[1]
        print("PH solver server encountered system error")
        print("Error: "+str(msg))
        print("Stack trace:")
        traceback.print_exc()
        exception_trapped = True
    except:
        print("Encountered unhandled exception")
        traceback.print_exc()
        exception_trapped = True

    # if an exception occurred, then we probably want to shut down all Pyro components.
    # otherwise, the PH client may have forever while waiting for results that will 
    # never arrive. there are better ways to handle this at the PH client level, but 
    # until those are implemented, this will suffice for cleanup.
    # NOTE: this should perhaps be command-line driven, so it can be disabled if desired.
    if exception_trapped == True:
        print("PH solver server aborted")
        shutDownPyroComponents()


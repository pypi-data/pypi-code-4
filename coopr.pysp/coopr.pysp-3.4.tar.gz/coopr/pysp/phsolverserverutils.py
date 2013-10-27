#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2012 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

# the intent of this module is to provide functions to interface from a 
# PH client to a set of PH solver servers.

import time
from coopr.pyomo import *

from six import iteritems, iterkeys
from six.moves import zip

class _PHServerConfig(object):

    # Transmit fixed variables
    transmit_fixed_vars       = 0b0001

    # Transmit PH Variables (unfixed).
    # Includes:
    #  - Non-leaf-stage ScenarioTree Variables
    #  - StageCost Variables
    #  - Quadratic Term Linearization Variables
    #  - Any variables required to evaluate the
    #    above cases when they are Expressions
    transmit_ph_vars          = 0b0010
    # Include leaf-stage variables in the above (unfixed)
    transmit_leaf_ph_vars     = 0b0110
    # Transmit Every Instance Variable (unfixed)
    transmit_all_vars         = 0b1110

    def __init__(self, transmit):
        self._transmit = transmit

    def TransmitFixedVars(self):
        return (self._transmit & self.transmit_fixed_vars) == self.transmit_fixed_vars

    def TransmitPHVars(self):
        return (self._transmit & self.transmit_ph_vars) == self.transmit_ph_vars

    def TransmitPHLeafVars(self):
        return (self._transmit & self.transmit_leaf_ph_vars) == self.transmit_leaf_ph_vars

    def TransmitAllVars(self):
        return (self._transmit & self.transmit_all_vars) == self.transmit_all_vars

# This version transmits ScenarioTree Variables,
# StageCost Variables (that are not Expressions), and
# Quadratic Linearization Variables added by PH
PHSolverServerConfigDefault = _PHServerConfig(_PHServerConfig.transmit_ph_vars)

# This version transmits all variables on the instance
# that are not fixed
#PHSolverServerConfigDefault = _PHServerConfig(_PHServerConfig.transmit_all_vars)

# This version transmits all variables on the instance
# INCLUDING fixed ones
#PHSolverServerConfigDefault = _PHServerConfig(_PHServerConfig.transmit_all_vars | _PHServerConfig.transmit_fixed_vars)

#
# The following helper functions transmit information about variables using a number
# of identifiers:
#
#    - InstanceID: A deterministic integer ID assigned to a model variable that will
#                  always match for two models with an identical variable set and
#                  whose variables have an identical declaration order in the model.
#
#    - ScenarioTreeID: An integer ID assigned to model variables tracked on the ScenarioTree.
#                      This ID may not be deterministic from run to run and will not match
#                      between ScenarioTrees on the master ph node and the ph solver servers.
#
#

#
# load results coming back from the Pyro PH solver server into the input instance.
# the input results are a dictionary of dictionaries, mapping variable name to
# dictionaries the first level; mapping indices to new values at the second level.
#

def load_component_values(block, values):

    phinst_sm_dict = block._PHInstanceSymbolMaps
    for ctype, ctype_values in iteritems(values):
        if ctype in phinst_sm_dict:
            ctype_sm_bySymbol = phinst_sm_dict[ctype].bySymbol
            if ctype is Var:
                for var_id, value in ctype_values:
                    vardata = ctype_sm_bySymbol[var_id] 
                    vardata.value = value
                    vardata.stale = False
            elif ctype is Expression:
                #
                # ***NOTE***: The underlying expressions will be replaced
                #             with numbers!
                #
                for expr_id, value in ctype_values:
                    exprdata = ctype_sm_bySymbol[expr_id]
                    exprdata.value = value
            #elif ctype is Suffix:
            #    for suffix_id, values in ctype_values:
            #        suffix = ctype_sm_bySymbol[suffix_id]
            #        suffix.updateValues(,
            #                            expand=False)
            else:
                raise NotImplementedError("Unhandled ctype %s encountered when loading "\
                                          "component values" % ctype)

#
# Sends a mapping between InstanceID and ScenarioTreeID so that
# phsolverservers are aware of the master nodes's ScenarioTreeID
# labeling. 
# *** Note ***: The scenario tree may hold references to
#               Expression components in the form of "Derived Variables"
#               for reporting. However, the function below only generates
#               the mapping for the Var components.
#

def extract_ids_maps(ph,scenario):

    scenario_instance = ph._instances[scenario._name]
    scenario_tree_sm_bySymbol = scenario_instance._ScenarioTreeSymbolMap.bySymbol
    var_phinst_sm_byObject = scenario_instance._PHInstanceSymbolMaps[Var].byObject

    ids_to_transmit = list((var_phinst_sm_byObject[id(component_data)], scenario_tree_id) \
                       for scenario_tree_id, component_data in iteritems(scenario_tree_sm_bySymbol) if (not component_data.is_expression()))

    return tuple(ids_to_transmit)

def collect_full_results(ph, var_config):
    
    start_time = time.time()

    if ph._verbose:
        print("Collecting results from PH solver servers")

    scenario_action_handle_map = {} # maps scenario names to action handles
    action_handle_scenario_map = {} # maps action handles to scenario names

    bundle_action_handle_map = {} # maps bundle names to action handles
    action_handle_bundle_map = {} # maps action handles to bundle names

    if ph._scenario_tree.contains_bundles():

        for scenario_bundle in ph._scenario_tree._scenario_bundles:

            new_action_handle =  ph._solver_manager.queue(action="collect_results",
                                                          name=scenario_bundle._name,
                                                          var_config=var_config)

            bundle_action_handle_map[scenario_bundle._name] = new_action_handle
            action_handle_bundle_map[new_action_handle] = scenario_bundle._name 

    else:

        for scenario in ph._scenario_tree._scenarios:

            new_action_handle = ph._solver_manager.queue(action="collect_results",
                                                         name=scenario._name,
                                                         var_config=var_config)

            scenario_action_handle_map[scenario._name] = new_action_handle
            action_handle_scenario_map[new_action_handle] = scenario._name


    if ph._scenario_tree.contains_bundles():

        if ph._verbose:
            print("Waiting for bundle results extraction")

        num_results_so_far = 0

        while (num_results_so_far < len(ph._scenario_tree._scenario_bundles)):

            bundle_action_handle = ph._solver_manager.wait_any()
            bundle_results = ph._solver_manager.get_results(bundle_action_handle)
            bundle_name = action_handle_bundle_map[bundle_action_handle]
                
            for scenario_name, instance_results in iteritems(bundle_results):
                load_component_values(ph._instances[scenario_name], instance_results)
 
            if ph._verbose:
                print("Successfully loaded solution for bundle="+bundle_name)

            num_results_so_far += 1
            
    else:

        if ph._verbose:
            print("Waiting for scenario results extraction")

        num_results_so_far = 0

        while (num_results_so_far < len(ph._scenario_tree._scenarios)):

            action_handle = ph._solver_manager.wait_any()
            results = ph._solver_manager.get_results(action_handle)
            scenario_name = action_handle_scenario_map[action_handle]
            instance = ph._instances[scenario_name]
            
            load_component_values(instance, results) 

            if ph._verbose:
                print("Successfully loaded solution for scenario="+scenario_name)

            num_results_so_far += 1


    end_time = time.time()

    if ph._output_times:
        print("Results collection time=%.2f seconds" % (end_time - start_time))

def transmit_scenario_tree_ids(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting ScenarioTree variable ids to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            ids_to_transmit = {}  # map from scenario name to the corresponding ids map

            for scenario in bundle._scenario_tree._scenarios:

                ids_to_transmit[scenario._name] = extract_ids_maps(ph,scenario)

            action_handles.append( ph._solver_manager.queue(action="update_scenario_tree_ids",
                                                            generateResponse=generate_responses,
                                                            name=bundle._name, 
                                                            new_ids=ids_to_transmit) )

    else:

        for scenario in ph._scenario_tree._scenarios:

            action_handles.append( ph._solver_manager.queue(action="update_scenario_tree_ids",
                                                            generateResponse=generate_responses,
                                                            name=scenario._name, 
                                                            new_ids=extract_ids_maps(ph,scenario)) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("ScenarioTree variable ids transmission time=%.2f seconds" % (end_time - start_time))

def extract_weight_maps(ph,scenario):

    # dictionaries of tuple of tuples. the first key is the parameter name, then we
    # have a tuple of (index,value) tuples.
    weights_to_transmit = {}

    scenario_instance = ph._instances[scenario._name]

    for tree_node in scenario._node_list[:-1]: # no blending over the final stage, so no weights to worry about.

        # the parameters we are transmitting have a fully populated index set - by
        # construction, there are no unused indices. thus, we can simple extract
        # the values in bulk, with no filtering.
        weight_parameter_name = "PHWEIGHT_"+tree_node._name

        # we don't use default values for the weight parameters in PH,
        # so iterate only over defined indicies.
        weights_to_transmit[weight_parameter_name] = tuple((index, data.value) \
                                                           for index,data in \
                                                           scenario_instance.find_component(weight_parameter_name).sparse_iteritems())

    return weights_to_transmit


def transmit_weights(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance weights to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            weights_to_transmit = {}  # map from scenario name to the corresponding weight map

            for scenario in bundle._scenario_tree._scenarios:

                weights_to_transmit[scenario._name] = extract_weight_maps(ph,scenario)

            action_handles.append( ph._solver_manager.queue(action="load_weights",
                                                            generateResponse=generate_responses,
                                                            name=bundle._name, 
                                                            new_weights=weights_to_transmit) )

    else:

        for scenario in ph._scenario_tree._scenarios:

            action_handles.append( ph._solver_manager.queue(action="load_weights",
                                                            generateResponse=generate_responses,
                                                            name=scenario._name, 
                                                            new_weights=extract_weight_maps(ph,scenario)) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Weight transmission time=%.2f seconds" % (end_time - start_time))

# TODO: Do something smart with xbars parameter updates since they are shared for bundle
#       and only need to be extracted once per node
def extract_xbar_maps(ph,scenario):

    # dictionaries of dictionaries. the first key is the parameter name. 
    # the second key is the index for the parameter. the value is the xbar.
    xbars_to_transmit = {}

    scenario_instance = ph._instances[scenario._name]

    for tree_node in scenario._node_list[:-1]: # no blending over the final stage, so no xbars to worry about.

        # the parameters we are transmitting have a fully populated index set - by
        # construction, there are no unused indices. thus, we can simple extract
        # the values in bulk, with no filtering.
        xbar_parameter_name = "PHXBAR_"+tree_node._name

        # we don't use default values for the xbar parameters in PH,
        # so iterate only over defined indicies.
        xbars_to_transmit[xbar_parameter_name] = tuple((index, data.value) \
                                                       for index, data in \
                                                       scenario_instance.find_component(xbar_parameter_name).sparse_iteritems())

    return xbars_to_transmit

# TODO: Do something smart with xbars parameter updates since they are shared for bundle
#       and only need to be extracted once per node
def transmit_xbars(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance xbars to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            xbars_to_transmit = {}  # map from scenario name to the corresponding xbar map

            for scenario in bundle._scenario_tree._scenarios:

                xbars_to_transmit[scenario._name] = extract_xbar_maps(ph,scenario)

            action_handles.append( ph._solver_manager.queue(action="load_xbars", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name, 
                                                            new_xbars=xbars_to_transmit) )

    else:

        for scenario in ph._scenario_tree._scenarios:

            action_handles.append( ph._solver_manager.queue(action="load_xbars",
                                                            generateResponse=generate_responses,
                                                            name=scenario._name, 
                                                            new_xbars=extract_xbar_maps(ph,scenario)) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Xbar transmission time=%.2f seconds" % (end_time - start_time))


#
# PH solver server initialization is a bit different than the other "transmit"-type functions
# in this file, in that it can take a non-trivial amount of time to create the instances,
# such that the main PH initialization routine can do unrelated work in parallel, and 
# synchronize on the action handles when it is done. thus, this function returns the 
# action handles for synchronization by the master PH process.
#

def initialize_ph_solver_servers(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting initialization information to PH solver servers")

    action_handles = []

    # both the dispatcher queue for initialization and the action name are "initialize" - might be confusing, but hopefully not so much.

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            action_handles.append( ph._solver_manager.queue(action="initialize", 
                                                            name="initialize",
                                                            model_directory=ph._model_directory_name, 
                                                            instance_directory=ph._instance_directory_name,
                                                            objective_sense=ph._objective_sense,
                                                            object_name=bundle._name, 
                                                            solver_type=ph._solver_type,
                                                            solver_io=ph._solver_io,
                                                            scenario_bundle_specification=ph._scenario_bundle_specification,
                                                            create_random_bundles=ph._create_random_bundles,
                                                            scenario_tree_random_seed=ph._scenario_tree_random_seed,
                                                            default_rho=ph._rho, 
                                                            linearize_nonbinary_penalty_terms=ph._linearize_nonbinary_penalty_terms,
                                                            retain_quadratic_binary_terms=ph._retain_quadratic_binary_terms,
                                                            drop_proximal_terms=ph._drop_proximal_terms,
                                                            breakpoint_strategy=ph._breakpoint_strategy,
                                                            integer_tolerance=ph._integer_tolerance,
                                                            verbose=ph._verbose) )
    else:

        for scenario in ph._scenario_tree._scenarios:

            action_handles.append( ph._solver_manager.queue(action="initialize", 
                                                            name="initialize",
                                                            model_directory=ph._model_directory_name, 
                                                            instance_directory=ph._instance_directory_name,
                                                            objective_sense=ph._objective_sense,
                                                            object_name=scenario._name, 
                                                            solver_type=ph._solver_type,
                                                            solver_io=ph._solver_io,
                                                            scenario_bundle_specification=None,
                                                            create_random_bundles=ph._create_random_bundles,
                                                            scenario_tree_random_seed=ph._scenario_tree_random_seed,
                                                            default_rho=ph._rho, 
                                                            linearize_nonbinary_penalty_terms=ph._linearize_nonbinary_penalty_terms,
                                                            retain_quadratic_binary_terms=ph._retain_quadratic_binary_terms,
                                                            drop_proximal_terms=ph._drop_proximal_terms,
                                                            breakpoint_strategy=ph._breakpoint_strategy,
                                                            integer_tolerance=ph._integer_tolerance,
                                                            verbose=ph._verbose) )

    end_time = time.time()

    if ph._output_times:
        print("Initialization transmission time=%.2f seconds" % (end_time - start_time))

    return action_handles

#
# a utility to extract the bounds for all variables in an instance.
#

def extract_bounds_map(ph, scenario_instance):

    var_phinst_sm_bySymbol = scenario_instance._PHInstanceSymbolMaps[Var].bySymbol

    bounds_to_transmit = tuple((instance_id, vardata.lb, vardata.ub)
                       for instance_id, vardata in iteritems(var_phinst_sm_bySymbol))
        
    return bounds_to_transmit

#
# a utility to transmit - across the PH solver manager - the current rho values for each problem instance. 
#

def transmit_bounds(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance variable bounds to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            bounds_to_transmit = {} # map from scenario name to the corresponding bounds map

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]                    

                bounds_to_transmit[scenario_name] = extract_bounds_map(ph, scenario_instance)

            action_handles.append( ph._solver_manager.queue(action="load_bounds", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name, 
                                                            new_bounds=bounds_to_transmit) )

    else:

        for scenario_name, scenario_instance in iteritems(ph._instances):

            action_handles.append( ph._solver_manager.queue(action="load_bounds", 
                                                            generateResponse=generate_responses,
                                                            name=scenario_name,
                                                            new_bounds=extract_bounds_map(ph, scenario_instance)) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Variable bound transmission time=%.2f seconds" % (end_time - start_time))

#
#
#

def extract_rho_map(ph, scenario):

    # a dictionary of dictionaries. the first key is the variable name.
    # the second key is the index for the particular rho. the value is the rho.
    rhos_to_transmit = {} 

    scenario_instance = ph._instances[scenario._name]

    for tree_node in scenario._node_list[:-1]: # no blending over the final stage, so no rhos to worry about.

        # the parameters we are transmitting have a fully populated index set - by
        # construction, there are no unused indices. thus, we can simple extract
        # the values in bulk, with no filtering.
        rho_parameter_name = "PHRHO_"+tree_node._name

        # we don't use default values for the rho parameters in PH,
        # so iterate only over defined indicies.
        rhos_to_transmit[rho_parameter_name] = tuple((index,data.value) \
                                                     for index, data in \
                                                     scenario_instance.find_component(rho_parameter_name).sparse_iteritems())

    return rhos_to_transmit

#
# a utility to transmit - across the PH solver manager - the current rho values for each problem instance. 
#

def transmit_rhos(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting instance rhos to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            rhos_to_transmit = {} # map from scenario name to the corresponding rho map

            for scenario in bundle._scenario_tree._scenarios:

                rhos_to_transmit[scenario._name] = extract_rho_map(ph,scenario)

            action_handles.append( ph._solver_manager.queue(action="load_rhos", 
                                                            name=bundle._name, 
                                                            generateResponse=generate_responses,
                                                            new_rhos=rhos_to_transmit) )

    else:

        for scenario in ph._scenario_tree._scenarios:

            action_handles.append( ph._solver_manager.queue(action="load_rhos", 
                                                            name=scenario._name, 
                                                            generateResponse=generate_responses,
                                                            new_rhos=extract_rho_map(ph,scenario)) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Rho transmission time=%.2f seconds" % (end_time - start_time))

#
# a utility to transmit - across the PH solver manager - the current scenario
# tree node statistics to each of my problem instances. done prior to each
# PH iteration k.
#

def transmit_tree_node_statistics(ph):

    # NOTE: A lot of the information here is redundant, as we are currently
    #       transmitting all information for all nodes to all solver servers,
    #       rather than information for the tree nodes associated with 
    #       scenarios for which a solver server is responsible.
    

    start_time = time.time()

    if ph._verbose:
        print("Transmitting tree node statistics to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            tree_node_minimums = {}
            tree_node_maximums = {}                

            # iterate over the tree nodes in the bundle scenario tree - but
            # there aren't any statistics there - be careful! 
            # TBD - we need to form these statistics! right now, they are 
            #       beyond the bundle.
            for bundle_tree_node in bundle._scenario_tree._tree_nodes:

                primary_tree_node = ph._scenario_tree._tree_node_map[bundle_tree_node._name]

                tree_node_minimums[primary_tree_node._name] = tuple(iteritems(primary_tree_node._minimums))
                tree_node_maximums[primary_tree_node._name] = tuple(iteritems(primary_tree_node._maximums))

            action_handles.append( ph._solver_manager.queue(action="load_tree_node_stats", 
                                                            name=bundle._name, 
                                                            generateResponse=generate_responses,
                                                            new_mins=tree_node_minimums, 
                                                            new_maxs=tree_node_maximums) )

    else:

        for scenario_name in ph._instances:

            tree_node_minimums = {}
            tree_node_maximums = {}

            scenario = ph._scenario_tree._scenario_map[scenario_name]

            for tree_node in scenario._node_list[:-1]:

                tree_node_minimums[tree_node._name] = tuple(iteritems(tree_node._minimums))
                tree_node_maximums[tree_node._name] = tuple(iteritems(tree_node._maximums))

            action_handles.append( ph._solver_manager.queue(action="load_tree_node_stats",
                                                            name=scenario_name, 
                                                            generateResponse=generate_responses,
                                                            new_mins=tree_node_minimums, 
                                                            new_maxs=tree_node_maximums) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Tree node statistics transmission time=%.2f seconds" % (end_time - start_time))


#
# a utility to activate - across the PH solver manager - weighted penalty objective terms.
#

def activate_ph_objective_weight_terms(ph):

    if ph._verbose:
        print("Transmitting request to activate PH objective weight terms to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="activate_ph_objective_weight_terms", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="activate_ph_objective_weight_terms", 
                                                            generateResponse=generate_responses,
                                                            name=scenario_name) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

#
# a utility to deactivate - across the PH solver manager - weighted penalty objective terms.
#

def deactivate_ph_objective_weight_terms(ph):

    if ph._verbose:
        print("Transmitting request to deactivate PH objective weight terms to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="deactivate_ph_objective_weight_terms", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="deactivate_ph_objective_weight_terms", 
                                                            generateResponse=generate_responses,
                                                            name=scenario_name) )
        
    if generate_responses:
        ph._solver_manager.wait_all(action_handles)


#
# a utility to activate - across the PH solver manager - proximal penalty objective terms.
#

def activate_ph_objective_proximal_terms(ph):

    if ph._verbose:
        print("Transmitting request to activate PH objective proximal terms to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="activate_ph_objective_proximal_terms", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="activate_ph_objective_proximal_terms", 
                                                            generateResponse=generate_responses,
                                                            name=scenario_name) )
        
    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

#
# a utility to deactivate - across the PH solver manager - proximal penalty objective terms.
#

def deactivate_ph_objective_proximal_terms(ph):

    if ph._verbose:
        print("Transmitting request to deactivate PH objective proximal terms to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="deactivate_ph_objective_proximal_terms", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="deactivate_ph_objective_proximal_terms", 
                                                            generateResponse=generate_responses,
                                                            name=scenario_name) )
        
    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

def transmit_fixed_variables(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting fixed variable status to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            fixed_variables_to_transmit = {} # map from scenario name to the corresponding list of fixed variables

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]                    

                fixed_variables_to_transmit[scenario_name] = ph._problem_states.fixed_variables[scenario_name]

            action_handles.append( ph._solver_manager.queue(action="fix_variables", 
                                                            name=bundle._name, 
                                                            generateResponse=generate_responses,
                                                            fixed_variables=fixed_variables_to_transmit) )

    else:

        for scenario_name in ph._instances:

            action_handles.append( ph._solver_manager.queue(action="fix_variables", 
                                                            name=scenario_name,
                                                            generateResponse=generate_responses,
                                                            fixed_variables=ph._problem_states.fixed_variables[scenario_name]) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Fixed variable transmission time=%.2f seconds" % (end_time - start_time))

def transmit_freed_variables(ph):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting freed variable status to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            freed_variables_to_transmit = {} # map from scenario name to the corresponding list of freed variables

            for scenario_name in bundle._scenario_names:

                scenario_instance = ph._instances[scenario_name]                    

                freed_variables_to_transmit[scenario_name] = ph._problem_states.freed_variables[scenario_name]

            action_handles.append( ph._solver_manager.queue(action="free_variables", 
                                                            name=bundle._name, 
                                                            generateResponse=generate_responses,
                                                            freed_variables=freed_variables_to_transmit) )

    else:

        for scenario_name in ph._instances:

            action_handles.append( ph._solver_manager.queue(action="free_variables", 
                                                            name=scenario_name, 
                                                            generateResponse=generate_responses,
                                                            freed_variables=ph._problem_states.freed_variables[scenario_name]) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("Freed variable transmission time=%.2f seconds" % (end_time - start_time))

def transmit_external_function_invocation(ph, module_name, function_name):

    start_time = time.time()

    if ph._verbose:
        print("Transmitting external function invocation request to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:

            action_handles.append( ph._solver_manager.queue(action="invoke_external_function", 
                                                            name=bundle._name, 
                                                            generateResponse=generate_responses,
                                                            module_name=module_name,
                                                            function_name=function_name) )

    else:

        for scenario_name in ph._instances:

            action_handles.append( ph._solver_manager.queue(action="invoke_external_function", 
                                                            name=scenario_name, 
                                                            generateResponse=generate_responses,
                                                            module_name=module_name,
                                                            function_name=function_name) )

    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

    end_time = time.time()

    if ph._output_times:
        print("External function invocation request transmission time=%.2f seconds" % (end_time - start_time))

#
# a utility to define model-level import suffixes - across the PH solver manager, on all instances.
#

def define_import_suffix(ph, suffix_name):

    if ph._verbose:
        print("Transmitting request to define suffix="+str(suffix_name)+" to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="define_import_suffix", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name,
                                                            suffix_name = suffix_name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="define_import_suffix", 
                                                            generateResponse=generate_responses,
                                                            name=scenario_name, 
                                                            suffix_name = suffix_name) )
        
    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

#
# a utility to request that each PH solver server restore solutions to their scenario instances.
#

def restore_cached_scenario_solutions(ph):

    if ph._verbose:
        print("Transmitting request to restore scenario solutions to PH solver servers")

    action_handles = []

    generate_responses = ph._handshake_with_phpyro

    if ph._scenario_tree.contains_bundles():

        for bundle in ph._scenario_tree._scenario_bundles:
            action_handles.append( ph._solver_manager.queue(action="restore_cached_scenario_solutions", 
                                                            generateResponse=generate_responses,
                                                            name=bundle._name) )
            
    else:

        for scenario_name in ph._instances:
            action_handles.append( ph._solver_manager.queue(action="restore_cached_scenario_solutions", 
                                                            generateResponse=generate_responses,
                                                            name=scenario_name) )
        
    if generate_responses:
        ph._solver_manager.wait_all(action_handles)

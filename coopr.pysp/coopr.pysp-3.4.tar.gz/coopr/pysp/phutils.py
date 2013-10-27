#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import traceback
import os
import itertools

from six import iteritems, itervalues

from coopr.pyomo import *
from coopr.opt import ProblemFormat
from coopr.pyomo.expr.linear_repn import linearize_model_expressions

from pyutilib.component.core import ExtensionPoint, Plugin

# for PYRO
try:
    import Pyro.core
    import Pyro.naming
    pyro_available = True
except:
    pyro_available = False

    
# these are the only two preprocessors currently invoked by 
# the simple_preprocessor, which in turn is invoked by the 
# preprocess() method of PyomoModel.
from coopr.pyomo.preprocess.compute_canonical_repn import preprocess_block_objectives as canonical_preprocess_block_objectives
from coopr.pyomo.preprocess.compute_canonical_repn import preprocess_block_constraints as canonical_preprocess_block_constraints
from coopr.pyomo.preprocess.compute_canonical_repn import preprocess_constraint as canonical_preprocess_constraint
from coopr.pyomo.preprocess.compute_ampl_repn import preprocess_block_objectives as ampl_preprocess_block_objectives
from coopr.pyomo.preprocess.compute_ampl_repn import preprocess_block_constraints as ampl_preprocess_block_constraints

canonical_expression_preprocessor = coopr.core.CooprAPIFactory("pyomo.model.compute_canonical_repn")

#
# Creates a deterministic symbol map for ctypes on a Block. This
# allows convenient transmission of information to and from PHSolverServers
# and makes it easy to save solutions using a pickleable list
# (symbol,values) tuples
#
def create_block_symbol_maps(owner_block, ctypes, recursive=True, update_new=False, update_all=False):
    """
    Inputs:
      - owner_block: A constructed Pyomo Block
      -      ctypes: An iterable of ctypes (or single ctype) to 
                     include in the _PHInstanceSymbolMaps dict
      -   recursive: Indicates whether to include ctypes contained on
                     subblocks in the given Block's SymbolMaps
      -  update_new: Update a possibly existing _PHInstanceSymbolMaps
                     dict on the owner_block with new ctypes. Any ctypes
                     given as inputs that already have existing SymbolMaps
                     will NOT be regenerated. **See: update_all
      -  update_all: Update a possibly existing _PHInstanceSymbolMaps
                     dict on the owner block with new ctypes, 
                     regenerating any existing ctypes given as inputs.
    Outputs: A dictionary (keys are ctypes) of SymbolMaps is placed on
             the owner_block and is named _PHInstanceSymbolMaps 
    """

    if owner_block.is_constructed() is False:
        raise ValueError("Failed to create _PHInstanceSymbolMap on Block %s. "\
                         "This Block has not been fully construced." % owner_block.cname(True))

    # The ctypes input may be iterable or a single type.
    # Either way turn it into a tuple of type(s)
    try:
        ctypes = tuple(ct for ct in ctypes)
    except TypeError:
        ctypes = (ctypes,)

    # Add the _PHInstanceSymbolMaps dict to the owner_block and
    # and warn if one already exists as it will be overwritten
    phinst_sm_dict = getattr(owner_block,"_PHInstanceSymbolMaps",None)
    if phinst_sm_dict is not None:
        if (update_new is False) and (update_all is False):
            print("***WARNING - Attribute with name _PHInstanceSymbolMaps already exists " \
                  "on Block %s. This Attribute will be overwritten" % owner_block.cname(True))
            phinst_sm_dict = owner_block._PHInstanceSymbolMaps = {}
        else:
            if type(phinst_sm_dict) is not dict:
                raise TypeError("Failed to update _PHInstanceSymbolMaps attribute "\
                                "on Block %s. Expected to find object with type %s "\
                                "but existing object is of type %s." % (owner_block.cname(True),
                                                                        dict,
                                                                        type(phinst_sm_dict)))
            
    else:
        phinst_sm_dict = owner_block._PHInstanceSymbolMaps = {}

    ctypes_to_generate = []
    for ctype in ctypes:
        if (ctype not in phinst_sm_dict) or (update_all is True):
            ctypes_to_generate.append(ctype)

    # Create a BasicSymbolMap for each ctype in the _PHInstanceSymbolMaps dict
    for ctype in ctypes_to_generate:
        phinst_sm_dict[ctype] = BasicSymbolMap()

    # Create the list of Blocks to iterator over. If this is recursive
    # turn the all_blocks() generator into a list, as we need to sort by
    # keys (for indexed blocks) so this process remains deterministic, 
    # and we don't want to sort more than necessary
    block_list = None
    if recursive is True:
        block_list = tuple(owner_block.all_blocks(sort_by_keys=True, sort_by_names=True))
    else:
        block_list = (owner_block,)

    for ctype in ctypes_to_generate:
        
        ctype_sm = phinst_sm_dict[ctype]
        bySymbol = ctype_sm.bySymbol
        cntr = 0
        
        for block in block_list:
            
            bySymbol.update(enumerate( \
                    subcomponents_data_generator(block, ctype, sort_by_keys=True, sort_by_names=True), \
                    cntr             ))
            cntr += len(bySymbol)-cntr+1
        
        ctype_sm.byObject = dict((id(component_data),symbol) for symbol,component_data in iteritems(bySymbol))


#
# a utility to scan through a scenario tree and set the variable values to None 
# for each variable not in the final stage that has not converged. necessary
# to avoid an illegal / infeasible warm-start for the extensive form solve.
#

def reset_nonconverged_variables(scenario_tree, scenario_instances):

   for stage in scenario_tree._stages[:-1]:

      for tree_node in stage._tree_nodes:
  
         for variable_id, var_datas in iteritems(tree_node._variable_datas):

             min_var_value = tree_node._minimums[variable_id]
             max_var_value = tree_node._maximums[variable_id]

             # TBD: THIS IS A HACK - GET THE THRESHOLD FROM SOMEWHERE AS AN INPUT ARGUMENT
             if (max_var_value - min_var_value) > 0.00001:

                 for var_data, probability in var_datas:

                     var_data.value = None
                     var_data.stale = True

#
# a utility to clear all cost variables - these are easily derived by the solvers,
# and can/will lead to infeasibilities unless everything is perfectly blended.
# in which case, you don't need to write the EF.
#

def reset_stage_cost_variables(scenario_tree, scenario_instances):

    for stage in scenario_tree._stages:
        for tree_node in stage._tree_nodes:
            for cost_var_data, scenario_probability in tree_node._cost_variable_datas:
                if cost_var_data.is_expression() is False:
                    cost_var_data.value = None
                    cost_var_data.stale = True

#
# a utility to clear the value of any PHQUADPENALTY* variables in the instance. these are
# associated with linearization, and if they are not cleared, can interfere with warm-starting
# due to infeasibilities.
#

def reset_linearization_variables(instance):

    for variable_name, variable in iteritems(instance.active_subcomponents(Var)):
        if variable_name.startswith("PHQUADPENALTY"):
            for var_value in itervalues(variable):
                var_value.value = None
                var_value.stale = True

#
# a utility for shutting down Pyro-related components, which at the
# moment is restricted to the name server and any dispatchers. the
# mip servers will come down once their dispatcher is shut down.
# NOTE: this is a utility that should eventually become part of
#       pyutilib.pyro, but because is prototype, I'm keeping it
#       here for now.
#

def shutDownPyroComponents():
    if not pyro_available:
        return

    Pyro.core.initServer()
    try:
        ns = Pyro.naming.NameServerLocator().getNS()
    except:
        print("***WARNING - Could not locate name server - Pyro PySP components will not be shut down")
        return
    ns_entries = ns.flatlist()
    for (name,uri) in ns_entries:
        if name == ":Pyro.NameServer":
            proxy = Pyro.core.getProxyForURI(uri)
            proxy._shutdown()
        elif name == ":PyUtilibServer.dispatcher":
            proxy = Pyro.core.getProxyForURI(uri)
            proxy.shutdown()

#
# a simple utility function to pretty-print an index tuple into a [x,y] form string.
#

def indexToString(index):

    if index is None:
        return ''

    # if the input type is a string or an int, then this isn't a tuple!
    if isinstance(index, (str, int)):
        return "["+str(index)+"]"

    result = "["
    for i in range(0,len(index)):
        result += str(index[i])
        if i != len(index) - 1:
            result += ","
    result += "]"
    return result

#
# a simple utility to determine if a variable name contains an index specification.
# in other words, is the reference to a complete variable (e.g., "foo") - which may
# or may not be indexed - or a specific index or set of indices (e.g., "foo[1]" or
# or "foo[1,*]".
#

def isVariableNameIndexed(variable_name):

    left_bracket_count = variable_name.count('[')
    right_bracket_count = variable_name.count(']')

    if (left_bracket_count == 1) and (right_bracket_count == 1):
        return True
    elif (left_bracket_count == 1) or (right_bracket_count == 1):
        raise ValueError("Illegally formed variable name="+variable_name+"; if indexed, variable names must contain matching left and right brackets")
    else:
        return False

#
# takes a string indexed of the form "('foo', 'bar')" and returns a proper tuple ('foo','bar')
#

def tupleizeIndexString(index_string):

    index_string=index_string.lstrip('(')
    index_string=index_string.rstrip(')')
    pieces = index_string.split(',')
    return_index = ()
    for piece in pieces:
        piece = piece.strip()
        piece = piece.lstrip('\'')
        piece = piece.rstrip('\'')
        transformed_component = None
        try:
            transformed_component = int(piece)
        except ValueError:
            transformed_component = piece
        return_index = return_index + (transformed_component,)

    # IMPT: if the tuple is a singleton, return the element itself.
    if len(return_index) == 1:
        return return_index[0]
    else:
        return return_index

#
# related to above, extract the index from the variable name.
# will throw an exception if the variable name isn't indexed.
# the returned variable name is a string, while the returned
# index is a tuple. integer values are converted to integers
# if the conversion works!
#

def extractVariableNameAndIndex(variable_name):

    if isVariableNameIndexed(variable_name) is False:
        raise ValueError("Non-indexed variable name passed to function extractVariableNameAndIndex()")

    pieces = variable_name.split('[')
    name = pieces[0].strip()
    full_index = pieces[1].rstrip(']')

    # even nested tuples in pyomo are "flattened" into
    # one-dimensional tuples. to accomplish flattening
    # replace all parens in the string with commas and
    # proceed with the split.
    full_index = full_index.replace("(",",").replace(")",",")
    indices = full_index.split(',')

    return_index = ()

    for index in indices:

        # unlikely, but strip white-space from the string.
        index=index.strip()

        # if the tuple contains nested tuples, then the nested
        # tuples have single quotes - "'" characters - around
        # strings. remove these, as otherwise you have an
        # illegal index.
        index = index.replace("\'","")

        # if the index is an integer, make it one!
        transformed_index = None
        try:
            transformed_index = int(index)
        except ValueError:
            transformed_index = index
        return_index = return_index + (transformed_index,)

    # IMPT: if the tuple is a singleton, return the element itself.
    if len(return_index) == 1:
        return name, return_index[0]
    else:
        return name, return_index

#
# determine if the input index is an instance of the template,
# which may or may not contain wildcards.
#

def indexMatchesTemplate(index, index_template):

    # if the input index is not a tuple, make it one.
    # ditto with the index template. one-dimensional
    # indices in pyomo are not tuples, but anything
    # else is.

    if type(index) != tuple:
        index = (index,)
    if type(index_template) != tuple:
        index_template = (index_template,)

    if len(index) != len(index_template):
        return False

    for i in xrange(0,len(index_template)):
        if index_template[i] == '*':
            # anything matches
            pass
        else:
            if index_template[i] != index[i]:
                return False

    return True

#
# given a variable (the real object, not the name) and an index,
# "shotgun" the index and see which variable indices match the
# input index. the cardinality could be > 1 if slices are
# specified, e.g., [*,1].
# 
# NOTE: This logic can be expensive for scenario trees with many
#       nodes, and for variables with many indices. thus, the 
#       logic behind the indexMatchesTemplate utility above
#       is in-lined in an efficient way here.
#

def extractVariableIndices(variable, index_template):

    variable_index_dimension = variable.dim()

    # do special handling for the case where the variable is
    # not indexed, i.e., of dimension 0. for singleton variables,
    # the mactch template can be the empty string, or - more
    # commonly, given that the empty string is hard to specify
    # in the scenario tree input data - a single wildcard character.
    if variable_index_dimension == 0:
       if (index_template != '') and (index_template != "*"):
          raise RuntimeError("Index template="+index_template+" specified for singleton variable="+variable.cname(True))

       return [None]

    # from this point on, we're dealing with indexed variables.
       
    # if the input index template is not a tuple, make it one.
    # one-dimensional indices in pyomo are not tuples, but 
    # everything else is.
    if type(index_template) != tuple:
       index_template = (index_template,)

    if variable_index_dimension != len(index_template):
        raise RuntimeError("Dimension="+str(len(index_template))+" of index template="+str(index_template)+" does match the dimension="+str(variable_index_dimension)+" of variable="+variable.cname(True))

    # cache for efficiency
    iterator_range = [i for i,match_str in enumerate(index_template) if match_str != '*']

    if len(iterator_range) == 0:
        return list(variable)

    result = []

    for index in variable:

        # if the input index is not a tuple, make it one for processing
        # purposes. however, return the original index always.
        if variable_index_dimension == 1:
           modified_index = (index,)
        else:
           modified_index = index

        match_found = True # until proven otherwise
        for i in iterator_range:
            if index_template[i] != modified_index[i]:
                match_found = False
                break

        if match_found is True:
            result.append(index)

    return result

#
# method to eliminate constraints from an input instance.
# TBD: really need to generalize the name, as we also cull
#      build actions and other stuff.
#
def cull_constraints_from_instance(model, constraints_to_retain):

    for block in model.all_blocks():
        for constraint_name, constraint in iteritems(block.subcomponents(Constraint)):
            if constraint_name not in constraints_to_retain:
                block.del_component(constraint_name)
        # Piecewise is a derived Block, so we have to look for it by sub-type.
        for constraint_name, constraint in iteritems(block.subcomponents(Block)):
            if isinstance(constraint, Piecewise) and (constraint_name not in constraints_to_retain):
                block.del_component(constraint_name)
        for constraint_name, constraint in iteritems(block.subcomponents(SOSConstraint)):
            if constraint_name not in constraints_to_retain:
                block.del_component(constraint_name)
        for action_name, action in iteritems(block.subcomponents(BuildAction)):
            if action_name not in constraints_to_retain:
                block.del_component(action_name)
        # Prevent any new constraints from being declared (e.g. during
        # construction of nested block models)
        block._suppress_ctypes.add(Constraint)
        block._suppress_ctypes.add(SOSConstraint)
        block._suppress_ctypes.add(Piecewise)
        block._suppress_ctypes.add(BuildAction)

#
# construct a scenario instance - just like it sounds!
#
def construct_scenario_instance(scenario_tree_instance,
                                scenario_data_directory_name,
                                scenario_name,
                                reference_model,
                                verbose,
                                preprocess = True,
                                linearize = True,
                                report_timing = False):

    if verbose is True:
        if scenario_tree_instance._scenario_based_data == 1:
            print("Scenario-based instance initialization enabled")
        else:
            print("Node-based instance initialization enabled")

    scenario = scenario_tree_instance.get_scenario(scenario_name)
    scenario_instance = None

    if verbose is True:
        print("Creating instance for scenario=" + scenario._name)

    try:
        if scenario_tree_instance._scenario_based_data == 1:
            scenario_data_filename = scenario_data_directory_name + os.sep + scenario._name
            # JPW: The following is a hack to support initialization of block instances,
            #      which don't work with .dat files at the moment. Actually, it's not that
            #      bad of a hack - it just needs to be extended a bit, and expanded into
            #      the node-based data read logic (where yaml is completely ignored at the 
            #      moment.
            if os.path.exists(scenario_data_filename+'.dat'):
                scenario_data_filename = scenario_data_filename + ".dat"
                data = None
            elif os.path.exists(scenario_data_filename+'.yaml'):
                import yaml
                scenario_data_filename = scenario_data_filename + ".yaml"
                yaml_input_file=open(scenario_data_filename,"r")
                data = yaml.load(yaml_input_file)
                yaml_input_file.close()
            else:
                raise RuntimeError("Cannot find the scenario data for " + scenario_data_filename)
            if verbose is True:
                print("Data for scenario=" + scenario._name + " loads from file=" + scenario_data_filename)
            if data is None:
                scenario_instance = reference_model.create(filename=scenario_data_filename, preprocess=preprocess, report_timing=report_timing)
            else:
                scenario_instance = reference_model.create(data, preprocess=preprocess, report_timing=report_timing)

        else:
            scenario_instance = reference_model.clone()

            data_files = []
            current_node = scenario._leaf_node
            while current_node is not None:
                node_data_filename = scenario_data_directory_name + os.sep + current_node._name + ".dat"
                if os.path.exists(node_data_filename) is False:
                    raise RuntimeError("Node data file="+node_data_filename+" does not exist or cannot be accessed")
                data_files.append(node_data_filename)
                current_node = current_node._parent

            # to make sure we read from root node to leaf node
            data_files.reverse()

            scenario_data = ModelData()
            for data_file in data_files:
                if verbose is True:
                    print("Node data for scenario=" + scenario._name + " partially loading from file=" + data_file)
                scenario_data.add(data_file)

            scenario_data.read(model=scenario_instance)
            scenario_instance.load(scenario_data)
            scenario_instance.concrete_mode()
            
            if preprocess is True:
                scenario_instance.preprocess()

        # apply each of the post-instance creation plugins. this really shouldn't be
        # associated (in terms of naming) with the pyomo script - this should be
        # rectified with a workflow re-work. it is unclear how this interacts, or 
        # doesn't, with the preprocessors.
        ep = ExtensionPoint(IPyomoScriptModifyInstance)
        for ep in ExtensionPoint(IPyomoScriptModifyInstance):
            ep.apply(options=None, model=reference_model, instance=scenario_instance)

    except Exception:
        exception = sys.exc_info()[1]
        raise RuntimeError("Failed to create model instance for scenario=" + scenario._name+"; Source error="+str(exception))

    if linearize is True:
        # IMPT: The model *must* be preprocessed in order for linearization to work. This is because
        #       linearization relies on the canonical expression representation extraction routine,
        #       which in turn relies on variables being identified/categorized (e.g., into "Used").
        scenario_instance.preprocess()
        linearize_model_expressions(scenario_instance)

    return scenario_instance

def update_all_rhos(instances, scenario_tree, rho_value=None, rho_scale=None):

    assert not ((rho_value is not None) and (rho_scale is not None))

    for stage in scenario_tree._stages[:-1]:
        
        for tree_node in stage._tree_nodes:

            rho_parameter_name = "PHRHO_"+variable_name

            for scenario in tree_node._scenarios:

                rho_parameter = scenario._instance.find_component(rho_parameter_name)

                for variable_id in tree_node._variable_ids:
                                        
                    if rho_value is not None:
                        rho_parameter[variable_id].value = rho_value
                    else:
                        rho_parameter[variable_id].value = rho_scale*rho_parameter[variable_id].value


# creates all PH parameters for a problem instance, given a scenario tree
# (to identify the relevant variables), a default rho (simply for initialization),
# and a boolean indicating if quadratic penalty terms are to be linearized.
# returns a list of any created variables, specifically when linearizing -
# this is useful to clean-up reporting.

def create_ph_parameters(instance, scenario_tree, default_rho, linearizing_penalty_terms):

    new_penalty_variable_names = []

    # gather all variables, and their corresponding indices, that are referenced
    # in any tree node corresponding to this scenario - with the exception of the
    # leaf tree node (where PH doesn't blend variables).
    instance_variables = {}  # map between variable names and sets of indices

    scenario = scenario_tree.get_scenario(instance.name)
    if scenario == None:
        raise RuntimeError("Scenario corresponding to instance name="+instance.name+" not present in scenario tree - could not create PH parameters for instance")

    for tree_node in scenario._node_list[:-1]:

        new_w_parameter_name = "PHWEIGHT_"+tree_node._name
        new_rho_parameter_name = "PHRHO_"+tree_node._name
        if linearizing_penalty_terms > 0:
            new_penalty_term_variable_name = "PHQUADPENALTY_"+tree_node._name

        nodal_index_set_name = "PHINDEX_"+tree_node._name
        nodal_index_set = instance.find_component(nodal_index_set_name)
        # TODO: This function requires calling create_nodal_ph_paramters first
        assert nodal_index_set is not None

        new_w_parameter = Param(nodal_index_set,name=new_w_parameter_name, default=0.0, nochecking=True, mutable=True)
        new_rho_parameter = Param(nodal_index_set,name=new_rho_parameter_name, default=0.0, nochecking=True, mutable=True)
        if linearizing_penalty_terms > 0:
            new_penalty_term_variable = Var(nodal_index_set,name=new_penalty_term_variable_name, bounds=(0.0,None))
        
        instance.add_component(new_w_parameter_name,new_w_parameter)
        instance.add_component(new_rho_parameter_name,new_rho_parameter)
        if linearizing_penalty_terms > 0:
            instance.add_component(new_penalty_term_variable_name, new_penalty_term_variable)
            new_penalty_variable_names.append(new_penalty_term_variable_name)

        new_w_parameter.store_values(0.0)
        new_rho_parameter.store_values(default_rho)

    return new_penalty_variable_names


# creates all PH node parameters for all instance, given a scenario tree

def create_nodal_ph_parameters(scenario_tree):

    for stage in scenario_tree._stages[:-1]:

        for tree_node in stage._tree_nodes:
            
            new_nodal_index_set_name = "PHINDEX_"+tree_node._name
            new_xbar_parameter_name = "PHXBAR_"+tree_node._name
            new_blend_parameter_name = "PHBLEND_"+tree_node._name
            
            # only create nodal index sets for non-derived variables.
            new_nodal_index_set = Set(name=new_nodal_index_set_name, initialize=list(tree_node._standard_variable_ids))

            for scenario in tree_node._scenarios:
                instance = scenario._instance

                # avoid the warnings generated by adding Set to multiple components, and
                # learn to live with the fact that these Params will point to some arbitrary instance
                # as their "parent" in the end
                new_nodal_index_set._parent = None

                # Add the shared parameter to the instance
                instance.add_component(new_nodal_index_set_name, new_nodal_index_set)

            new_xbar_parameter = Param(new_nodal_index_set, name=new_xbar_parameter_name, default=0.0, nochecking=True, mutable=True)
            new_blend_parameter = Param(new_nodal_index_set, name=new_blend_parameter_name, within=Binary, default=False, nochecking=True, mutable=True)

            for scenario in tree_node._scenarios:
                instance = scenario._instance

                # avoid the warnings generated by adding Param to multiple components, and
                # learn to live with the fact that these Params will point to some arbitrary instance
                # as their "parent" in the end
                new_xbar_parameter._parent = None
                new_blend_parameter._parent = None

                # Add the shared parameter to the instance
                instance.add_component(new_xbar_parameter_name,new_xbar_parameter)
                instance.add_component(new_blend_parameter_name,new_blend_parameter)
                
            new_xbar_parameter.store_values(0.0)
            new_blend_parameter.store_values(1)

def preprocess_scenario_instance(scenario_instance, 
                                 instance_variables_fixed,
                                 instance_variables_freed,
                                 instance_user_constraints_modified, 
                                 instance_ph_constraints_modified, 
                                 instance_ph_constraints,
                                 instance_objective_modified, 
                                 preprocess_fixed_variables,
                                 solver):

    if (not instance_objective_modified) and (not instance_variables_fixed) and \
       (not instance_variables_freed) and (not instance_ph_constraints_modified) and \
       (not instance_user_constraints_modified): 

        # the condition of "nothing modified" should only be triggered at PH iteration 0. instances are
        # already preprocessed following construction, and there isn't any augmentation of the objective 
        # function yet.
        return

    if (instance_objective_modified is True):
        # if only the objective changed, there is minimal work to do - 
        # just recompute the associated repn
        if solver.problem_format() == ProblemFormat.nl:
            ampl_preprocess_block_objectives(scenario_instance)
        else:
            canonical_preprocess_block_objectives(scenario_instance, None)
        
    if (instance_variables_fixed or instance_variables_freed) and (preprocess_fixed_variables):
        
        if solver.problem_format() == ProblemFormat.nl:
            ampl_preprocess_block_objectives(scenario_instance)
            for block in scenario_instance.all_blocks():
                ampl_preprocess_block_constraints(block)
        else:
            canonical_expression_preprocessor({}, model=scenario_instance)

        # We've preprocessed the entire instance, no point in checking anything else
        return

    if instance_user_constraints_modified is True:
        if solver.problem_format() == ProblemFormat.nl:
            for block in scenario_instance.all_blocks():
                ampl_preprocess_block_constraints(block)
        else:
            var_id_map = {}
            for block in scenario_instance.all_blocks():
                canonical_preprocess_block_constraints(block, var_id_map)

    elif (instance_ph_constraints_modified is True):

        # only pre-process the piecewise constraints
        if solver.problem_format() == ProblemFormat.nl:
            ampl_preprocess_block_constraints(scenario_instance)
        else:
            var_id_map = {}
            for constraint_name in instance_ph_constraints:
                canonical_preprocess_constraint(scenario_instance, getattr(scenario_instance, constraint_name), var_id_map=var_id_map)

#
# Extracts an active objective from the instance (top-level only). 
# Works with index objectives that may have all but one index 
# deactivated. safety_checks=True asserts that exactly ONE active objective
# is found on the top-level instance.
#

def find_active_objective(instance, safety_checks=False):
    
    if safety_checks is False:
        # NON-RECURSIVE (when JDS makes that change to generators)
        for objective_data in active_subcomponents_data_generator(instance,Objective):
            # Return the first active objective encountered
            return objective_data
    else:
        # NON-RECURSIVE (when JDS makes that change to generators)
        objectives = []
        for objective_data in active_subcomponents_data_generator(instance,Objective):
            objectives.append(objective_data)
        if len(objectives) > 1:
            names = [o.cname(True) for o in objectives]
            raise AssertionError("More than one active objective was found on instance %s: %s" % (instance.cname(True), names))
        if len(objectives) > 0:
            return objectives[0]
    return None



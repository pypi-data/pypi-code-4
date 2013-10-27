#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys
import random
import weakref

from math import fabs, ceil

from coopr.pyomo import *
from coopr.pysp.phutils import *
from coopr.pyomo.base import BasicSymbolMap, CounterLabeler

from six import iterkeys, iteritems, itervalues, advance_iterator, PY3
from six.moves import xrange
using_py3 = PY3

class ScenarioTreeNode(object):

    """ Constructor
    """
    def __init__(self, name, conditional_probability, stage):

        # self-explanatory!
        self._name = name

        # the stage to which this tree node belongs.
        self._stage = stage

        # defines the tree structure
        self._parent = None

        # a collection of ScenarioTreeNodes
        self._children = [] 

        # conditional on parent
        self._conditional_probability = conditional_probability

        # a collection of all Scenario objects passing through this node in the tree
        self._scenarios = [] 

        # the cumulative probability of scenarios at this node.
        # cached for efficiency.
        self._probability = 0.0

        # information relating to all variables blended at this node, whether
        # of the standard or derived varieties.
        self._variable_ids = {} # maps id -> (name, index)
        self._name_index_to_id = {} # maps (name,index) -> id
        self._variable_datas = {} # maps id -> list of (vardata,probability) across all scenarios

        # keep track of the variable indices at this node, independent of type.
        # this is useful for iterating. maps variable name to a list of indices.
        self._variable_indices = {}

        # variables are either standard or derived - but not both.
        # partition the ids into two sets, as we deal with these
        # differently in algorithmic and reporting contexts.
        self._standard_variable_ids = set()
        self._derived_variable_ids = set()

        # a list of _VarData objects, representing the cost variables for
        # each scenario passing through this tree node.
        self._cost_variable_datas = []

        # general use statistics for the variables at each node.
        # each attribute is a map between the variable name and a
        # parameter (over the same index set) encoding the corresponding
        # statistic computed over all scenarios for that node. the
        # parameters are named as the source variable name suffixed
        # by one of: "NODEMIN", "NODEAVG", and "NODEMAX".
        # NOTE: the averages are probability_weighted - the min/max
        #       values are not.
        # NOTE: the parameter names are basically irrelevant, and the
        #       convention is assumed to be enforced by whoever populates
        #       these parameters.
        self._minimums = {}
        self._averages = {}
        self._maximums = {}
        self._xbars = {} # NODEXBAR
        self._wbars = {} # NODEWBAR
        self._fixed = set() # a set of node variables ids that are fixed

        # solution (variable) values for this node. assumed to be distinct
        # from self._averages, as the latter are not necessarily feasible.
        # keys are variable ids.
        self._solution = {}

    #
    # given a set of scenario instances, compute the set of indices for 
    # non-anticipative variables at this node, as defined by the input
    # match templates.
    #

    def updateVariableIndicesAndValues(self, variable_name, match_templates, 
                                       derived=False, id_labeler=None, name_index_to_id_map=None):

        # ensure that the variable exists on each scenario instance, and 
        # that there is at least one index match per template.

        # To avoid calling extractVariableIndices more than necessary we take the
        # last scenario in the next loop as our "representative" scenario from 
        # which we use the new_match_indices list
        new_match_indices = None
        var_component = {}
        symbolmap = {}
        scenario = None
        for scenario in self._scenarios:

            scenario_instance = scenario._instance

            instance_variable = scenario_instance.find_component(variable_name)
            if instance_variable is None:
                raise RuntimeError("The component=" + variable_name + " associated with stage=" + self._stage._name + " is not present in instance=" + scenario_instance.name)

            if derived is False:
                if not instance_variable.type() is Var:
                    raise RuntimeError("The component=" + variable_name + " associated with stage=" + self._stage._name + " is present in instance=" + scenario_instance.name + " but is not a variable - type="+str(type(instance_variable)) + "!")
            else:
                if not instance_variable.type() in (Var, Expression):
                    raise RuntimeError("The derived component=" + variable_name + " associated with stage=" + self._stage._name + " is present in instance=" + scenario_instance.name + " but is not a Var or Expression - type="+str(type(instance_variable)) + "!")

            if instance_variable is None:
                raise ValueError("Variable=" + variable_name + " associated with stage=" + self._stage._name + " is not present in instance=" + scenario_instance.name+"; scenario tree construction failed")

            new_match_indices = []

            for match_template in match_templates:

                indices = extractVariableIndices(instance_variable, match_template)

                # validate that at least one of the indices in the variable matches to the template - otherwise, the template is bogus.
                # with one exception: if the variable is empty (the index set is empty), then don't warn - the instance was designed this way.
                if (len(indices) == 0) and (len(instance_variable) > 0):
                    raise ValueError("No indices match template="+str(match_template)+" for variable=" + variable_name + " in scenario=" + scenario._name)

                new_match_indices.extend(indices)

            var_component[scenario._name] = scenario_instance.find_component(variable_name)

            if (id_labeler is not None) or (name_index_to_id_map is not None):
                # Tag each instance with a ScenarioTreeSymbolMap. This will allow us to identify
                # common blended variables within a node across scenario instances without 
                # having to do an expensive name lookup each time.
                # TODO: Replace all tree node dictionary keys and PySP parameters from name/index lookups
                # to start using this scenario tree integer id. This should provide significant speed
                # but will be somewhat large undertaking.
                this_symbolmap = getattr(scenario_instance,"_ScenarioTreeSymbolMap", None)
                if this_symbolmap is None:
                    this_symbolmap = scenario_instance._ScenarioTreeSymbolMap = BasicSymbolMap()
                symbolmap[scenario._name] = this_symbolmap

        # find a representative scenario instance belonging to (or passing 
        # through) this node in the tree. the first scenario is as good as any.
        # NOTE: At some point we should check that the index sets across all 
        #       scenarios at a node actually match for each variable.

        self._variable_indices.setdefault(variable_name, []).extend(new_match_indices)

        if (id_labeler is not None) or (name_index_to_id_map is not None):

            for index in sorted(new_match_indices):

                # create the ScenarioTree integer id for this variable across all scenario 
                # instances, or look it up if a map has been provided.
                scenario_tree_id = None
                if id_labeler != None:
                    scenario_tree_id = id_labeler()
                elif name_index_to_id_map != None:
                    scenario_tree_id = name_index_to_id_map[variable_name, index]

                if derived == False:
                    self._standard_variable_ids.add(scenario_tree_id)
                else:
                    self._derived_variable_ids.add(scenario_tree_id)

                self._variable_ids[scenario_tree_id] = (variable_name,index)
                self._name_index_to_id[(variable_name,index)] = scenario_tree_id
                self._variable_datas[scenario_tree_id] = []
                for scenario in self._scenarios:
                    vardata = var_component[scenario._name][index]
                    symbolmap[scenario._name].updateSymbol(vardata,scenario_tree_id)
                    self._variable_datas[scenario_tree_id].append((vardata, scenario._probability))
            
    #
    # same as the above, but specialized to cost variables.
    #

    def updateCostVariableIndexAndValue(self, cost_variable_name, cost_variable_index):

        # ensure that the cost variable exists on each scenario instance, and that the index is valid.
        # if so, add it to the list of _VarDatas for scenarios at this tree node.
        for scenario in self._scenarios:
            scenario_instance = scenario._instance        
            cost_variable = scenario_instance.find_component(cost_variable_name)

            if cost_variable is None:
                raise ValueError("Cost variable=" + cost_variable_name + " associated with stage=" + self._stage._name + " is not present in model=" + scenario_instance.name+"; scenario tree construction failed")
            if not cost_variable.type() in [Var,Expression]:
                raise RuntimeError("The component=" + cost_variable_name + " associated with stage=" + self._stage._name + " is present in model=" + scenario_instance.name + " but is not a variable or expression - type="+str(cost_variable.type()) + "!")
            if cost_variable_index not in cost_variable:
                raise RuntimeError("The index "+str(cost_variable_index)+" is not defined for cost variable=" + cost_variable_name + " on model=" + scenario_instance.name)

            self._cost_variable_datas.append((cost_variable[cost_variable_index],scenario._probability))


    
    #
    # given a set of scenario instances, compute the set of indices being
    # blended for each variable at this node. populates the _variable_indices
    # and _variable_values attributes of a tree node.
    #

    def populateVariableIndicesAndValues(self, id_labeler=None, name_index_to_id_map=None):

        self._variable_indices = {}
        self._variable_datas = {}
        self._standard_variable_ids = set()
        self._derived_variable_ids = set()

        stage_variables = self._stage._variables
        for variable_name in sorted(iterkeys(stage_variables)):
            self.updateVariableIndicesAndValues(variable_name, stage_variables[variable_name], 
                                                derived=False, id_labeler=id_labeler, name_index_to_id_map=name_index_to_id_map)

        stage_derived_variables = self._stage._derived_variables
        for variable_name in sorted(iterkeys(stage_derived_variables)):
            self.updateVariableIndicesAndValues(variable_name, stage_derived_variables[variable_name], 
                                                derived=True, id_labeler=id_labeler, name_index_to_id_map=name_index_to_id_map)

        self.updateCostVariableIndexAndValue(self._stage._cost_variable[0], self._stage._cost_variable[1])

    #
    # copies the parameter values values from the _averages attribute
    # into the _solution attribute - only for active variable values.
    # for leaf nodes, simply copies the values from the _VarValue objects
    # at that node - because there are no statistics maintained.
    #

    def snapshotSolutionFromAverages(self):

        self._solution = {}

        if self.is_leaf_node():
            
            # NOTE: The var data tuple at a leaf node will only contain a single element.
            self._solution.update((variable_id, var_datas[0][0].value) for variable_id, var_datas in iteritems(self._variable_datas))

        else:
                
            self._solution.update(self._averages)

    #
    # computes the solution values from the composite scenario instances at this tree node.
    #

    def snapshotSolutionFromInstances(self):

        self._solution = {}

        for variable_id in self._standard_variable_ids:

            var_datas = self._variable_datas[variable_id]
            # the following loop is just a sanity check.
            for var_data, scenario_probability in var_datas:
                if (var_data.stale is True) and (var_data.fixed is False): # a variable that is fixed will be flagged as unused.
                    variable_name, index = self._variable_ids[variable_id]
                    print("CAUTION: Encountered variable="+variable_name+indexToString(index)+" that is not in use within scenario="+self._name+", but the scenario tree specification indicates that non-anticipativity is to be enforced; the variable should either be eliminated from the model or from the scenario tree specification.")
                
            # if a variable is stale, it could be because it is fixed - in which case, we want to snapshot the average value.
            avg = sum(scenario_probability * value(var_data) for var_data, scenario_probability in var_datas if (var_data.stale is False) or (var_data.fixed is True))

            # the node probability is allowed to be zero in the scenario tree specification.
            # this is useful in cases where one wants to temporarily ignore certain scenarios.
            # in this case, just skip reporting of variables for that node.
            if self._probability > 0.0:
                avg /= self._probability

            self._solution[variable_id] = avg

        for variable_id in self._derived_variable_ids:

            var_datas = self._variable_datas[variable_id]

            avg = sum(scenario_probability * value(var_data) for var_data, scenario_probability in var_datas)

            # the node probability is allowed to be zero in the scenario tree specification.
            # this is useful in cases where one wants to temporarily ignore certain scenarios.
            # in this case, just skip reporting of variables for that node.
            if self._probability > 0.0:
                avg /= self._probability

            self._solution[variable_id] = avg

    #
    # a utility to compute the cost of the current node plus the expected costs of child nodes.
    #

    def computeExpectedNodeCost(self):

        # IMPT: This implicitly assumes convergence across the scenarios - if not, garbage results.
        my_cost = value(self._cost_variable_datas[0][0])
        child_cost = 0.0
        for child in self._children:
            child_cost += (child._conditional_probability * child.computeExpectedNodeCost())
        return my_cost + child_cost

    # 
    # a simple predicate to check if this tree node belongs to the last stage in the scenario tree.
    #
    def is_leaf_node(self):
        
        return self._stage.is_last_stage()

    # 
    # a utility to determine if the input variable name/index pair is a derived variable.
    # 
    def is_derived_variable(self, variable_name, variable_index):
        return (variable_name, variable_index) in self._name_index_to_id

    # 
    # a utility to extract the value for the input name/index pair.
    # 
    def get_variable_value(self, name, index):

        try:
            variable_id = self._name_index_to_id[(name,index)]
        except KeyError:
            raise ValueError("No ID for variable="+str(name)+", index="+str(index)+" is defined for scenario tree node="+self._name)

        try:
            return self._solution[variable_id]
        except KeyError:
            raise ValueError("No value for variable="+str(name)+", index="+str(index)+" is defined for scenario tree node="+self._name)

    # 
    # fix the indicated input variable / index pair to the input value.
    #
    def fix_variable(self, variable_id, fix_value):

        self._fixed.add(variable_id)

        for var_data, scenario_probability in self._variable_datas[variable_id]:
            var_data.fixed = True
            var_data.value = fix_value


    # 
    # free the indicated input variable / index pair to the input value.
    #
    def free_variable(self, variable_id):

        if variable_id in self._fixed:
            self._fixed.remove(variable_id)
            for var_data, scenario_probability in self._variable_datas[variable_id]:
                var_data.fixed = False

class ScenarioTreeStage(object):

    """ Constructor
    """
    def __init__(self, *args, **kwds):

        self._name = ""

        # a collection of ScenarioTreeNode objects associated with this stage.
        self._tree_nodes = []

        # the parent scenario tree for this stage.
        self._scenario_tree = None

        # a map between a variable name and a list of original index match templates, specified as strings. 
        # we want to maintain these for a variety of reasons, perhaps the most important being that for 
        # output purposes. specific indices that match belong to the tree node, as that may be specific to 
        # a tree node.
        self._variables = {}

        # same as above, but for derived stage variables.
        self._derived_variables = {}

        # a tuple consisting of (1) the name of the variable that stores the stage-specific cost 
        # in all scenarios and  (2) the corresponding index *string* - this is converted in the tree 
        # node to a real index.
        self._cost_variable = (None, None)

    #
    # add a new variable to the stage, which will include updating the solution maps for 
    # each associated ScenarioTreeNode. 
    #
    def add_variable(self, variable_name, new_match_template, create_variable_ids=True):

        labeler = None
        if create_variable_ids is True:
            labeler = self._scenario_tree._id_labeler

        existing_match_templates = self._variables.setdefault(variable_name, [])
        existing_match_templates.append(new_match_template)

        for tree_node in self._tree_nodes:
            tree_node.updateVariableIndicesAndValues(variable_name, new_match_template, 
                                                     derived=False,
                                                     id_labeler=labeler)

    # 
    # a simple predicate to check if this stage is the last stage in the scenario tree.
    #
    def is_last_stage(self):
        
        return self == self._scenario_tree._stages[-1]

class Scenario(object):

    """ Constructor
    """
    def __init__(self, *args, **kwds):

        self._name = None
        self._leaf_node = None  # allows for construction of node list
        self._node_list = []    # sequence from parent to leaf of ScenarioTreeNodes
        self._probability = 0.0 # the unconditional probability for this scenario, computed from the node list
        self._instance = None   # the Pyomo instance corresponding to this scenario.
        self._instance_cost_expression = None
        self._instance_objective = None

class ScenarioTreeBundle(object):

     def __init__(self, *args, **kwds):
       
         self._name = None
         self._scenario_names = []
         self._scenario_tree = None # This is a compressed scenario tree, just for the bundle.
         self._probability = 0.0 # the absolute probability of scenarios associated with this node in the scenario tree.

class ScenarioTree(object):

    # a utility to construct scenario bundles.
    def _construct_scenario_bundles(self, scenario_tree_instance):

        for bundle_name in scenario_tree_instance.Bundles:
           scenario_list = []
           bundle_probability = 0.0
           for scenario_name in scenario_tree_instance.BundleScenarios[bundle_name]:
              scenario_list.append(scenario_name)              
              bundle_probability += self._scenario_map[scenario_name]._probability

           scenario_tree_instance.Bundling[None] = False # to stop recursion!
           
           scenario_tree_for_bundle = ScenarioTree(scenariotreeinstance=scenario_tree_instance,
                                                   scenariobundlelist=scenario_list)

           scenario_tree_instance.Bundling[None] = True

           if scenario_tree_for_bundle.validate() is False:
               raise RuntimeError("***ERROR: Bundled scenario tree is invalid!!!")

           new_bundle = ScenarioTreeBundle()
           new_bundle._name = bundle_name
           new_bundle._scenario_names = scenario_list
           new_bundle._scenario_tree = scenario_tree_for_bundle
           new_bundle._probability = bundle_probability

           self._scenario_bundles.append(new_bundle)
           self._scenario_bundle_map[new_bundle._name] = new_bundle

    #
    # a utility to construct the stage objects for this scenario tree.
    # operates strictly by side effects, initializing the self
    # _stages and _stage_map attributes.
    #

    def _construct_stages(self, stage_names, stage_variable_names, stage_cost_variable_names, stage_derived_variable_names):

        # construct the stage objects, which will leave them
        # largely uninitialized - no variable information, in particular.
        for stage_name in stage_names:

            new_stage = ScenarioTreeStage()
            new_stage._name = stage_name
            new_stage._scenario_tree = self

            for variable_string in stage_variable_names[stage_name]:
                if isVariableNameIndexed(variable_string) is True:
                    variable_name, match_template = extractVariableNameAndIndex(variable_string)                
                else:
                    variable_name = variable_string
                    match_template = ""
                if variable_name not in new_stage._variables:
                    new_stage._variables[variable_name] = []
                new_stage._variables[variable_name].append(match_template)

            for variable_string in stage_derived_variable_names[stage_name]:
                if isVariableNameIndexed(variable_string) is True:
                    variable_name, match_template = extractVariableNameAndIndex(variable_string)                
                else:
                    variable_name = variable_string
                    match_template = ""
                if variable_name not in new_stage._derived_variables:
                    new_stage._derived_variables[variable_name] = []
                new_stage._derived_variables[variable_name].append(match_template)

            # de-reference is required to access the parameter value
            cost_variable_string = value(stage_cost_variable_names[stage_name]) 
            if isVariableNameIndexed(cost_variable_string) is True:
                cost_variable_name, cost_variable_index = extractVariableNameAndIndex(cost_variable_string)
            else:
                cost_variable_name = cost_variable_string
                cost_variable_index = None
            new_stage._cost_variable = (cost_variable_name, cost_variable_index)

            self._stages.append(new_stage)
            self._stage_map[stage_name] = new_stage


    """ Constructor
        Arguments:
            scenarioinstance     - the reference (deterministic) scenario instance.
            scenariotreeinstance - the pyomo model specifying all scenario tree (text) data.
            scenariobundlelist   - a list of scenario names to retain, i.e., cull the rest to create a reduced tree!
    """
    def __init__(self, *args, **kwds):

        self._name = None # some arbitrary identifier

        # should be called once for each variable blended across a node
        self._id_labeler = CounterLabeler()

        # the core objects defining the scenario tree.
        self._tree_nodes = [] # collection of ScenarioTreeNodes
        self._stages = [] # collection of ScenarioTreeStages - assumed to be in time-order. the set (provided by the user) itself *must* be ordered.
        self._scenarios = [] # collection of Scenarios
        self._scenario_bundles = [] # collection of ScenarioTreeBundles

        # dictionaries for the above.
        self._tree_node_map = {}
        self._stage_map = {}
        self._scenario_map = {}
        self._scenario_bundle_map = {}

        # a boolean indicating how data for scenario instances is specified.
        # possibly belongs elsewhere, e.g., in the PH algorithm.
        self._scenario_based_data = None

        scenario_tree_instance = kwds.pop( 'scenariotreeinstance', None )
        scenario_bundle_list = kwds.pop( 'scenariobundlelist', None )

        # process the keyword options
        for key in kwds:
            sys.stderr.write("Unknown option '%s' specified in call to ScenarioTree constructor\n" % key)

        if scenario_tree_instance is None:
            raise ValueError("A scenario tree instance must be supplied in the ScenarioTree constructor")

        node_ids = scenario_tree_instance.Nodes
        node_child_ids = scenario_tree_instance.Children
        node_stage_ids = scenario_tree_instance.NodeStage
        node_probability_map = scenario_tree_instance.ConditionalProbability
        stage_ids = scenario_tree_instance.Stages
        stage_variable_ids = scenario_tree_instance.StageVariables
        stage_cost_variable_ids = scenario_tree_instance.StageCostVariable
        stage_derived_variable_ids = scenario_tree_instance.StageDerivedVariables
        scenario_ids = scenario_tree_instance.Scenarios
        scenario_leaf_ids = scenario_tree_instance.ScenarioLeafNode
        scenario_based_data = scenario_tree_instance.ScenarioBasedData

        # save the method for instance data storage.
        self._scenario_based_data = scenario_based_data()

        # the input stages must be ordered, for both output purposes and knowledge of the final stage.
        if stage_ids.ordered is False:
            raise ValueError("An ordered set of stage IDs must be supplied in the ScenarioTree constructor")

        empty_nonleaf_stages = [stage for stage in stage_ids \
                                    if len(stage_variable_ids[stage])==0 \
                                    and stage != stage_ids.last()]
        if len(empty_nonleaf_stages) > 0:
            raise ValueError("A ScenarioTree has been declared with one"
                             " or more empty (non-leaf) stages. This must"
                             " be corrected by defining non-empty sets "
                             "for the following entries in "
                             "ScenarioStructure.dat: \n- %s" % \
                              ('\n- '.join('StageVariables[%s]'%(stage) \
                              for stage in empty_nonleaf_stages)))

        #
        # construct the actual tree objects
        #

        # construct the stage objects w/o any linkages first; link them up
        # with tree nodes after these have been fully constructed.
        self._construct_stages(stage_ids, stage_variable_ids, stage_cost_variable_ids, stage_derived_variable_ids)

        # construct the tree node objects themselves in a first pass,
        # and then link them up in a second pass to form the tree.
        # can't do a single pass because the objects may not exist.
        for tree_node_name in node_ids:

            if tree_node_name not in node_stage_ids:
                raise ValueError("No stage is assigned to tree node=" + tree_node._name)

            stage_name = value(node_stage_ids[tree_node_name])
            if stage_name not in iterkeys(self._stage_map):
                raise ValueError("Unknown stage=" + stage_name + " assigned to tree node=" + tree_node._name)

            new_tree_node = ScenarioTreeNode(tree_node_name,
                                             value(node_probability_map[tree_node_name]),
                                             self._stage_map[stage_name])

            self._tree_nodes.append(new_tree_node)
            self._tree_node_map[tree_node_name] = new_tree_node
            self._stage_map[stage_name]._tree_nodes.append(new_tree_node)

        # link up the tree nodes objects based on the child id sets.
        for this_node in self._tree_nodes:
            this_node._children = []
            if this_node._name in node_child_ids: # otherwise, you're at a leaf and all is well.
                child_ids = node_child_ids[this_node._name]
                for child_id in child_ids:
                    if child_id in self._tree_node_map:
                        child_node = self._tree_node_map[child_id]
                        this_node._children.append(child_node)
                        if child_node._parent is None:
                            child_node._parent = this_node
                        else:
                            raise ValueError("Multiple parents specified for tree node="+child_id+"; existing parent node="+child_node._parent._name+"; conflicting parent node="+this_node._name)
                    else:
                        raise ValueError("Unknown child tree node=" + child_id + " specified for tree node=" + this_node._name)

        # at this point, the scenario tree nodes and the stages are set - no
        # two-pass logic necessary when constructing scenarios.
        for scenario_name in scenario_ids:

            # IMPT: the name of the scenario is assumed to have no '_' (underscore) characters in the identifier.
            #       this is required when writing the extensive form, e.g., the scenario is used in the extensive
            #       form as a prefix on variable and constraint names. this convention simplifies parsing on the
            #       back end; if the underscore isn't used as a reserved character, then some other separator
            #       symbol would be required, or we would have to engage in some complex prefix matching with
            #       all possible scenario names.
            if scenario_name.count("_") != 0:
                raise ValueError("By convention, scenario names in PySP cannot contain underscore (_) characters; the scenario in violation="+scenario_name)

            new_scenario = Scenario()
            new_scenario._name=scenario_name

            if scenario_name not in iterkeys(scenario_leaf_ids):
                raise ValueError("No leaf tree node specified for scenario=" + scenario_name)
            else:
                scenario_leaf_node_name = value(scenario_leaf_ids[scenario_name])
                if scenario_leaf_node_name not in self._tree_node_map:
                    raise ValueError("Uknown tree node=" + scenario_leaf_node_name + " specified as leaf of scenario=" + scenario_name)
                else:
                    new_scenario._leaf_node = self._tree_node_map[scenario_leaf_node_name]

            current_node = new_scenario._leaf_node
            while current_node is not None:
                new_scenario._node_list.append(current_node)
                current_node._scenarios.append(new_scenario) # links the scenarios to the nodes to enforce necessary non-anticipativity
                current_node = current_node._parent
            new_scenario._node_list.reverse()
            # This now loops root -> leaf
            probability = 1.0
            for current_node in new_scenario._node_list:
                probability *= current_node._conditional_probability
                # NOTE: The line placement below is a little weird, in that
                #       it is embedded in a scenario loop - so the probabilities
                #       for some nodes will be redundantly computed. But this works.
                current_node._probability = probability
            new_scenario._probability = probability

            self._scenarios.append(new_scenario)
            self._scenario_map[scenario_name] = new_scenario
        
        # for output purposes, it is useful to known the maximal length of identifiers
        # in the scenario tree for any particular category. I'm building these up
        # incrementally, as they are needed. 0 indicates unassigned.
        self._max_scenario_id_length = 0

        # does the actual traversal to populate the members.
        self.computeIdentifierMaxLengths()

        # if a sub-bundle of scenarios has been specified, mark the
        # active scenario tree components and compress the tree.
        if scenario_bundle_list is not None:
            self.compress(scenario_bundle_list)

        # NEW SCENARIO BUNDLING STARTS HERE
        if value(scenario_tree_instance.Bundling[None]) is True:
           self._construct_scenario_bundles(scenario_tree_instance)

    # 
    # populate those portions of the scenario tree and associated stages and
    # tree nodes that reference the scenario instances associated with the 
    # tree.
    #

    def linkInInstances(self, scenario_instance_map, objective_sense=None, create_variable_ids=True, master_scenario_tree=None):

        if (master_scenario_tree is not None) and (objective_sense is not None):
            raise ValueError("An objective sense for an autogenerated objective can not be used when a master ScenarioTree is specified")

        if objective_sense not in (minimize, maximize, None):
            raise ValueError("Invalid value (%r) for objective sense given to the linkInInstances method. "
                               "Choices are: [minimize, maximize, None]" % (objective_sense))

        if (create_variable_ids == True) and (master_scenario_tree is not None):
            raise RuntimeError("The linkInInstances method of ScenarioTree objects cannot be invoked with both create_variable_ids=True and master_scenario_tree!=None")

        # propagate the scenario instances to the scenario tree object structure.
        # NOTE: The input scenario instances may be a super-set of the 
        #       set of Scenario objects for this ScenarioTree.
        for scenario_name, scenario_instance in iteritems(scenario_instance_map):
            if self.contains_scenario(scenario_name):
                scenario = self.get_scenario(scenario_name)
                scenario._instance = scenario_instance
        
        # link the scenario tree object structures to the instance components.
        self.populateVariableIndicesAndValues(create_variable_ids=create_variable_ids,
                                              master_scenario_tree=master_scenario_tree)

        # create the scenario cost expression to be used for the objective
        if master_scenario_tree is None:
            for scenario_name, scenario_instance in iteritems(scenario_instance_map):
                if self.contains_scenario(scenario_name):
                    user_objective = find_active_objective(scenario_instance, safety_checks=True)
                    if objective_sense is None:
                        if user_objective is None:
                            raise RuntimeError("An active Objective could not be found on instance for scenario %s." % (scenario_name))
                        cost_expr_name = "_USER_COST_EXPRESSION_"+scenario_name
                        cost_expr = Expression(name=cost_expr_name,initialize=user_objective.expr)
                        scenario_instance.add_component(cost_expr_name,cost_expr)
                        scenario._instance_cost_expression = cost_expr
                        
                        user_objective_sense = minimize if (user_objective.is_minimizing()) else maximize
                        cost_obj_name = "_USER_COST_OBJECTIVE_"+scenario_name
                        cost_obj = Objective(name=cost_obj_name,expr=cost_expr, sense=user_objective_sense)
                        scenario_instance.add_component(cost_obj_name,cost_obj)
                        scenario._instance_objective = cost_obj
                        user_objective.deactivate()
                    else:
                        if user_objective is not None:
                            #print("* Active Objective \"%s\" on scenario instance \"%s\" will not be used. "
                            #                       % (user_objective.cname(True),scenario_name))
                            user_objective.deactivate()
                        scenario = self.get_scenario(scenario_name)
                        
                        cost = 0.0
                        for stage in self._stages:
                            stage_cost_var = scenario_instance.find_component(stage._cost_variable[0])[stage._cost_variable[1]]
                            cost += stage_cost_var
                        cost_expr_name = "_PYSP_COST_EXPRESSION_"+scenario_name
                        cost_expr = Expression(name=cost_expr_name,initialize=cost)
                        scenario_instance.add_component(cost_expr_name,cost_expr)
                        scenario._instance_cost_expression = cost_expr
                        
                        cost_obj_name = "_PYSP_COST_OBJECTIVE_"+scenario_name
                        cost_obj = Objective(name=cost_obj_name,expr=cost_expr, sense=objective_sense)
                        scenario_instance.add_component(cost_obj_name,cost_obj)
                        scenario._instance_objective = cost_obj
        else:
            for scenario_name, scenario_instance in iteritems(scenario_instance_map):
                if self.contains_scenario(scenario_name):
                    scenario = self.get_scenario(scenario_name)
                    master_scenario = master_scenario_tree.get_scenario(scenario_name)
                    scenario._instance_cost_expression = master_scenario._instance_cost_expression
                    scenario._instance_objective = master_scenario._instance_objective
                    

    #
    # compute the set of variable indices being blended at each node. this can't be done
    # until all of the scenario instances are available, as different scenarios can have
    # different index sets.
    #

    def populateVariableIndicesAndValues(self, create_variable_ids=True, master_scenario_tree=None):

        if (create_variable_ids == True) and (master_scenario_tree != None):
            raise RuntimeError("The populateVariableIndicesAndValues method of ScenarioTree objects cannot be invoked with both create_variable_ids=True and master_scenario_tree!=None")

        labeler = None
        if create_variable_ids is True:
            labeler = self._id_labeler

        for stage in self._stages:
            if using_py3:
                tree_node_list = sorted(stage._tree_nodes, key=lambda x: x._name)
            else:
                tree_node_list = sorted(stage._tree_nodes, cmp=lambda x,y: x._name < y._name)
            for tree_node in tree_node_list:
                name_index_to_id_map = None
                if master_scenario_tree is not None:
                    name_index_to_id_map = master_scenario_tree.get_node(tree_node._name)._name_index_to_id
                tree_node.populateVariableIndicesAndValues(id_labeler=labeler,
                                                           name_index_to_id_map=name_index_to_id_map)

    #
    # is the indicated scenario / bundle in the tree?
    #

    def contains_scenario(self, name):
        return name in self._scenario_map

    def contains_bundles(self):
        return len(self._scenario_bundle_map) > 0

    def contains_bundle(self, name):
        return name in self._scenario_bundle_map

    #
    # get the scenario / bundle object from the tree.
    #

    def get_scenario(self, name):
        return self._scenario_map[name]

    def get_bundle(self, name):
        return self._scenario_bundle_map[name]
    
    # there are many contexts where manipulators of a scenario
    # tree simply need an arbitrary scenario to proceed...
    def get_arbitrary_scenario(self):
        return self._scenarios[0]

    #
    # get the scenario tree node object from the tree
    # 
    
    def get_node(self, name):
        return self._tree_node_map[name]

    #
    # compute the scenario cost for the input instance, i.e.,
    # the sum of all stage cost variables.
    #

    def compute_scenario_cost(self, instance):
        aggregate_cost = 0.0
        for stage in self._stages:
            instance_cost_variable = instance.find_component(stage._cost_variable[0])[stage._cost_variable[1]]
            if instance_cost_variable.value is not None:
                    # depending on the situation (and the model), the stage cost variables might not have values.
                aggregate_cost += instance_cost_variable
        return aggregate_cost

    #
    # utility for compressing or culling a scenario tree based on
    # a provided list of scenarios (specified by name) to retain -
    # all non-referenced components are eliminated. this particular
    # method compresses *in-place*, i.e., via direct modification
    # of the scenario tree structure.
    #

    def compress(self, scenario_bundle_list):

        # scan for and mark all referenced scenarios and
        # tree nodes in the bundle list - all stages will
        # obviously remain.
        for scenario_name in scenario_bundle_list:
            if scenario_name not in self._scenario_map:
                raise ValueError("Scenario="+scenario_name+" selected for bundling not present in scenario tree")
            scenario = self._scenario_map[scenario_name]
            scenario.retain = True

            # chase all nodes comprising this scenario,
            # marking them for retention.
            for node in scenario._node_list:
                node.retain = True

        # scan for any non-retained scenarios and tree nodes.
        scenarios_to_delete = []
        tree_nodes_to_delete = []
        for scenario in self._scenarios:
            if hasattr(scenario, "retain") is True:
                delattr(scenario, "retain")
            else:
                scenarios_to_delete.append(scenario)
                del self._scenario_map[scenario._name]

        for tree_node in self._tree_nodes:
            if hasattr(tree_node, "retain") is True:
                delattr(tree_node, "retain")
            else:
                tree_nodes_to_delete.append(tree_node)
                del self._tree_node_map[tree_node._name]

        # JPW does not claim the following routines are
        # the most efficient. rather, they get the job
        # done while avoiding serious issues with
        # attempting to remove elements from a list that
        # you are iterating over.

        # delete all references to unmarked scenarios
        # and child tree nodes in the scenario tree node
        # structures.
        for tree_node in self._tree_nodes:
            for scenario in scenarios_to_delete:
                if scenario in tree_node._scenarios:
                    tree_node._scenarios.remove(scenario)
            for node_to_delete in tree_nodes_to_delete:
                if node_to_delete in tree_node._children:
                    tree_node._children.remove(node_to_delete)

        # delete all references to unmarked tree nodes
        # in the scenario tree stage structures.
        for stage in self._stages:
            for tree_node in tree_nodes_to_delete:
                if tree_node in stage._tree_nodes:
                    stage._tree_nodes.remove(tree_node)

        # delete all unreferenced entries from the core scenario
        # tree data structures.
        for scenario in scenarios_to_delete:
            self._scenarios.remove(scenario)
        for tree_node in tree_nodes_to_delete:
            self._tree_nodes.remove(tree_node)

        # re-normalize the conditional probabilities of the
        # children at each tree node.
        for tree_node in self._tree_nodes:
            sum_child_probabilities = 0.0
            for child_node in tree_node._children:
                sum_child_probabilities += child_node._conditional_probability
            for child_node in tree_node._children:
                child_node._conditional_probability = child_node._conditional_probability / sum_child_probabilities

        # re-compute the absolute scenario probabilities based
        # on the re-normalized conditional node probabilities.
        for scenario in self._scenarios:
            probability = 1.0
            for tree_node in scenario._node_list:
                probability = probability * tree_node._conditional_probability
            scenario._probability = probability

        # now that we've culled the scenarios, cull the bundles. do this in two
        # passes. in the first pass, we identify the names of bundles to delete,
        # by looking for bundles with deleted scenarios. in the second pass,
        # we delete the bundles from the scenario tree, and normalize the 
        # probabilities of the remaining bundles.
        bundles_to_delete = [] # indices of the objects in the scenario tree bundle list
        for i in xrange(0,len(self._scenario_bundles)):
            scenario_bundle = self._scenario_bundles[i]
            for scenario_name in scenario_bundle._scenario_names:
                if scenario_name not in self._scenario_map:
                    bundles_to_delete.append(i)
                    break
        bundles_to_delete.reverse()
        for i in bundles_to_delete:
            deleted_bundle = self._scenario_bundles.pop(i)
            del self._scenario_bundle_map[deleted_bundle._name]

        sum_bundle_probabilities = sum(bundle._probability for bundle in self._scenario_bundles)
        for bundle in self._scenario_bundles:
            bundle._probability /= sum_bundle_probabilities

    #
    # utility for automatically selecting a proportion of scenarios from the
    # tree to retain, eliminating the rest.
    #

    def downsample(self, fraction_to_retain, random_seed, verbose=False):

        random.seed(random_seed)

        random_sequence=range(len(self._scenarios))
        random.shuffle(random_sequence)

        number_to_retain = max(int(round(float(len(random_sequence)*fraction_to_retain))), 1)

        scenario_bundle_list = []
        for i in xrange(number_to_retain):
            scenario_bundle_list.append(self._scenarios[random_sequence[i]]._name)

        if verbose is True:
            print("Downsampling scenario tree - retained scenarios: "+str(scenario_bundle_list))

        self.compress(scenario_bundle_list)


    #
    # returns the root node of the scenario tree
    #

    def findRootNode(self):

        for tree_node in self._tree_nodes:
            if tree_node._parent is None:
                return tree_node
        return None

    #
    # a utility function to compute, based on the current scenario tree content,
    # the maximal length of identifiers in various categories.
    #

    def computeIdentifierMaxLengths(self):

        self._max_scenario_id_length = 0
        for scenario in self._scenarios:
            if len(scenario._name) > self._max_scenario_id_length:
                self._max_scenario_id_length = len(scenario._name)

    #
    # a utility function to (partially, at the moment) validate a scenario tree
    #

    def validate(self):

        # for any node, the sum of conditional probabilities of the children should sum to 1.
        for tree_node in self._tree_nodes:
            sum_probabilities = 0.0
            if len(tree_node._children) > 0:
                for child in tree_node._children:
                    sum_probabilities += child._conditional_probability
                if abs(1.0 - sum_probabilities) > 0.000001:
                    print("The child conditional probabilities for tree node=" + tree_node._name + " sum to " + str(sum_probabilities))
                    return False

        # ensure that there is only one root node in the tree
        num_roots = 0
        root_ids = []
        for tree_node in self._tree_nodes:
            if tree_node._parent is None:
                num_roots += 1
                root_ids.append(tree_node._name)

        if num_roots != 1:
            print("Illegal set of root nodes detected: " + str(root_ids))
            return False

        # there must be at least one scenario passing through each tree node.
        for tree_node in self._tree_nodes:
            if len(tree_node._scenarios) == 0:
                print("There are no scenarios associated with tree node=" + tree_node._name)
                return False

        return True

    #
    # copies the parameter values stored in any tree node _averages attribute
    # into any tree node _solution attribute - only for active variable values.
    #

    def snapshotSolutionFromAverages(self):

        for tree_node in self._tree_nodes:

            tree_node.snapshotSolutionFromAverages()

    #
    # assigns the variable values at each tree node based on the input instances.
    #

    def snapshotSolutionFromInstances(self):

        for tree_node in self._tree_nodes:
            tree_node.snapshotSolutionFromInstances()

    #
    # a utility to determine the stage to which the input variable belongs.
    # this is horribly inefficient, in the absence of an inverse map. fortunately,
    # it isn't really called that often (yet). stage membership is determined
    # by comparing the input variable name with the reference instance
    # variable name (which is what the scenario tree refers to) and the
    # associated indices.
    #

    def variableStage(self, variable, index):

        # NOTE: The logic below is bad, in the sense that the looping should
        #       really be over tree nodes - a stage in isolation doesn't make
        #       any sense at all. ultimately, this will involve by-passing the
        #       extractVariableIndices logic, and moving toward iteration over
        #       the tree nodes within a stage.
        for stage in self._stages:
            for stage_variable_name, match_template in iteritems(stage._variables):
                if (variable.name == stage_variable_name):
                    match_indices = extractVariableIndices(variable, match_template[0])
                    if ((index is None) and (len(match_indices)==0)) or (index in match_indices):
                        return stage

            # IMPT: this is a temporary hack - the real fix is to force users to
            # have every variable assigned to some stage in the model, either
            # automatically or explicitly.
            if (variable.name == stage._cost_variable[0]):
                return stage

        raise RuntimeError("The variable="+str(variable.name)+", index="+str(index)+" does not belong to any stage in the scenario tree")

    #
    # a utility to determine the stage to which the input constraint "belongs".
    # a constraint belongs to the latest stage in which referenced variables
    # in the constraint appears in that stage.
    # input is a constraint is of type "Constraint", and an index of that
    # constraint - which might be None in the case of singleton constraints.
    # currently doesn't deal with SOS constraints, for no real good reason.
    # returns an instance of a ScenarioTreeStage object.
    # IMPT: this method works on the canonical representation ("repn" attribute)
    #       of a constraint. this implies that pre-processing of the instance
    #       has been performed.
    # NOTE: there is still the issue of whether the contained variables really
    #       belong to the same model, but that is a different issue we won't
    #       address right now (e.g., what does it mean for a constraint in an
    #       extensive form binding instance to belong to a stage?).
    #

    def constraintStage(self, constraint, index):

        largest_stage_index = -1
        largest_stage = None

        parent_instance = constraint.parent()
        parent_repn_suffix = parent_instance.subcomponent("canonical_repn")

        canonical_repn = parent_repn_suffix.getValue(constraint[index])
        if canonical_repn == None:
            raise RuntimeError("***ERROR: Method constraintStage in class ScenarioTree encountered a constraint with no canonical representation - was preprocessing performed?")

        if isinstance(canonical_repn, GeneralCanonicalRepn):
            raise RuntimeError("***ERROR: Method constraintStage in class ScenarioTree encountered a constraint with a general canonical encoding - only linear canonical encodings are expected!")

        for var_data in canonical_repn.variables:

            var_stage = self.variableStage(var_data.component(), var_data.index())
            var_stage_index = self._stages.index(var_stage)

            if var_stage_index > largest_stage_index:
                largest_stage_index = var_stage_index
                largest_stage = var_stage

        return largest_stage

    #
    # method to create random bundles of scenarios - like the name says!
    #

    def create_random_bundles(self, scenario_tree_instance, num_bundles, random_seed):

        random.seed(random_seed)

        num_scenarios = len(self._scenarios)

        sequence = range(num_scenarios)
        random.shuffle(sequence)

        scenario_tree_instance.Bundling[None] = True

        bundle_size = int(ceil(num_scenarios / num_bundles))

        next_scenario_index = 0

        # this is a hack-ish way to re-initialize the Bundles
        # set of a scenario tree instance, which should already
        # be there (because it is defined in the abstract model).
        # however, we don't have a "clear" method on a set, so...
        scenario_tree_instance.del_component("Bundles")
        scenario_tree_instance.add_component("Bundles", Set())
        for i in xrange(1, num_bundles+1):
            bundle_name = "Bundle"+str(i)
            scenario_tree_instance.Bundles.add(bundle_name)

        # ditto above comment regarding del_component/add_component
        scenario_tree_instance.del_component("BundleScenarios")
        scenario_tree_instance.add_component("BundleScenarios", Set(scenario_tree_instance.Bundles))

        for i in xrange(1, num_bundles+1):
            bundle_name = "Bundle"+str(i)
            scenario_tree_instance.BundleScenarios[bundle_name] = Set()
            for j in xrange(1,bundle_size+1):
                scenario_name = self._scenarios[sequence[next_scenario_index]]._name
                scenario_tree_instance.BundleScenarios[bundle_name].add(scenario_name)
                next_scenario_index+=1
        for i in xrange(next_scenario_index, num_scenarios):
            scenario_name = self._scenarios[sequence[next_scenario_index]]._name
            scenario_tree_instance.BundleScenarios[bundle_name].add(scenario_name)
            next_scenario_index+=1

        self._construct_scenario_bundles(scenario_tree_instance)

    #
    # a utility function to pretty-print the static/non-cost information associated with a scenario tree
    #

    def pprint(self):

        print("Scenario Tree Detail")

        print("----------------------------------------------------")
        print("Tree Nodes:")
        print("")
        for tree_node_name in sorted(iterkeys(self._tree_node_map)):
            tree_node = self._tree_node_map[tree_node_name]
            print("\tName=" + tree_node_name)
            if tree_node._stage is not None:
                print("\tStage=" + str(tree_node._stage._name))
            else:
                print("\t Stage=None")
            if tree_node._parent is not None:
                print("\tParent=" + tree_node._parent._name)
            else:
                print("\tParent=" + "None")
            if tree_node._conditional_probability is not None:
                print("\tConditional probability=%4.4f" % tree_node._conditional_probability)
            else:
                print("\tConditional probability=" + "***Undefined***")
            print("\tChildren:")
            if len(tree_node._children) > 0:
                for child_node in sorted(tree_node._children, key=lambda x: x._name):
                    print("\t\t" + child_node._name)
            else:
                print("\t\tNone")
            print("\tScenarios:")
            if len(tree_node._scenarios) == 0:
                print("\t\tNone")
            else:
                for scenario in sorted(tree_node._scenarios, key=lambda x: x._name):
                    print("\t\t" + scenario._name)
            print("")
        print("----------------------------------------------------")
        print("Stages:")
        for stage_name in sorted(iterkeys(self._stage_map)):
            stage = self._stage_map[stage_name]
            print("\tName=" + str(stage_name))
            print("\tTree Nodes: ")
            for tree_node in sorted(stage._tree_nodes, key=lambda x: x._name):
                print("\t\t" + tree_node._name)
            if len(stage._variables) > 0:
                print("\tVariables: ")
                for variable_name in sorted(iterkeys(stage._variables)):
                    match_templates = stage._variables[variable_name]
                    sys.stdout.write("\t\t "+variable_name+" : ")
                    for match_template in match_templates:
                       sys.stdout.write(indexToString(match_template)+' ')
                    print("")
            if len(stage._derived_variables) > 0:
                print("\tDerived Variables: ")
                for variable_name in sorted(iterkeys(stage._derived_variables)):
                    match_templates = stage._derived_variables[variable_name]
                    sys.stdout.write("\t\t "+variable_name+" : ")
                    for match_template in match_templates:
                       sys.stdout.write(indexToString(match_template)+' ')
                    print("")
            print("\tCost Variable: ")
            if stage._cost_variable[1] is None:
                print("\t\t" + stage._cost_variable[0])
            else:
                print("\t\t" + stage._cost_variable[0] + indexToString(stage._cost_variable[1]))
            print("")
        print("----------------------------------------------------")
        print("Scenarios:")
        for scenario_name in sorted(iterkeys(self._scenario_map)):
            scenario = self._scenario_map[scenario_name]
            print("\tName=" + scenario_name)
            print("\tProbability=%4.4f" % scenario._probability)
            if scenario._leaf_node is None:
                print("\tLeaf node=None")
            else:
                print("\tLeaf node=" + scenario._leaf_node._name)
            print("\tTree node sequence:")
            for tree_node in scenario._node_list:
                print("\t\t" + tree_node._name)
            print("")
        print("----------------------------------------------------")
        if len(self._scenario_bundles) > 0:
            print("Scenario Bundles:")
            for bundle_name in sorted(iterkeys(self._scenario_bundle_map)):
                scenario_bundle = self._scenario_bundle_map[bundle_name]
                print("\tName=" + bundle_name)
                print("\tProbability=%4.4f" % scenario_bundle._probability            )
                sys.stdout.write("\tScenarios:  ")
                for scenario_name in sorted(scenario_bundle._scenario_names):
                    sys.stdout.write(scenario_name+' ')
                sys.stdout.write("\n")
                print("")
            print("----------------------------------------------------")

    #
    # a utility function to pretty-print the solution associated with a scenario tree
    #

    def pprintSolution(self, epsilon=1.0e-5):

        print("----------------------------------------------------")
        print("Tree Nodes:")
        print("")
        for tree_node_name in sorted(iterkeys(self._tree_node_map)):
            tree_node = self._tree_node_map[tree_node_name]
            print("\tName=" + tree_node_name)
            if tree_node._stage is not None:
                print("\tStage=" + tree_node._stage._name)
            else:
                print("\t Stage=None")
            if tree_node._parent is not None:
                print("\tParent=" + tree_node._parent._name)
            else:
                print("\tParent=" + "None")
            if len(tree_node._stage._variables) > 0:
                print("\tVariables: ")
                for variable_name, match_template in iteritems(tree_node._stage._variables):
                    indices = sorted(tree_node._variable_indices[variable_name])
                    for index in indices:
                        id = tree_node._name_index_to_id[variable_name,index]
                        if id in tree_node._standard_variable_ids:
                            value = tree_node._solution[id]
                            if (value is not None) and (fabs(value) > epsilon):
                                print("\t\t"+variable_name+indexToString(index)+"="+str(value))
            if len(tree_node._stage._derived_variables) > 0:
                print("\tDerived Variables: ")
                for variable_name, match_template in iteritems(tree_node._stage._derived_variables):
                    indices = sorted(tree_node._variable_indices[variable_name])
                    for index in indices:
                        id = tree_node._name_index_to_id[variable_name,index]
                        if id in tree_node._derived_variable_ids:
                            value = tree_node._solution[tree_node._name_index_to_id[variable_name,index]]
                            if (value is not None) and (fabs(value) > epsilon):
                                print("\t\t"+variable_name+indexToString(index)+"="+str(value))
            print("")

    #
    # a utility function to pretty-print the cost information associated with a scenario tree
    #

    def pprintCosts(self, scenario_instance_map):

        print("Scenario Tree Costs")
        print("***CAUTION***: Assumes full (or nearly so) convergence of scenario solutions at each node in the scenario tree - computed costs are invalid otherwise")

        print("----------------------------------------------------")
        print("Tree Nodes:")
        print("")
        for tree_node_name in sorted(iterkeys(self._tree_node_map)):
            tree_node = self._tree_node_map[tree_node_name]
            print("\tName=" + tree_node_name)
            if tree_node._stage is not None:
                print("\tStage=" + tree_node._stage._name)
            else:
                print("\t Stage=None")
            if tree_node._parent is not None:
                print("\tParent=" + tree_node._parent._name)
            else:
                print("\tParent=" + "None")
            if tree_node._conditional_probability is not None:
                print("\tConditional probability=%4.4f" % tree_node._conditional_probability)
            else:
                print("\tConditional probability=" + "***Undefined***")
            print("\tChildren:")
            if len(tree_node._children) > 0:
                for child_node in sorted(tree_node._children, key=lambda x: x._name):
                    print("\t\t" + child_node._name)
            else:
                print("\t\tNone")
            print("\tScenarios:")
            if len(tree_node._scenarios) == 0:
                print("\t\tNone")
            else:
                for scenario in sorted(tree_node._scenarios, key=lambda x: x._name):
                    print("\t\t" + scenario._name)
            print("\tExpected node cost=%10.4f" % tree_node.computeExpectedNodeCost())
            print("")

        print("----------------------------------------------------")
        print("Scenarios:")
        print("")
        for scenario_name, scenario in sorted(iteritems(self._scenario_map)):
            instance = scenario_instance_map[scenario_name]

            print("\tName=" + scenario_name)
            print("\tProbability=%4.4f" % scenario._probability)

            if scenario._leaf_node is None:
                print("\tLeaf Node=None")
            else:
                print("\tLeaf Node=" + scenario._leaf_node._name)

            print("\tTree node sequence:")
            for tree_node in scenario._node_list:
                print("\t\t" + tree_node._name)

            aggregate_cost = 0.0
            for stage in self._stages:
                # find the tree node for this scenario, representing this stage.
                tree_node = None
                for node in scenario._node_list:
                    if node._stage == stage:
                        tree_node = node
                        break

                # n-squared - could be easily fixed if it becomes an issue.
                cost_variable_value = None
                for var_value, scenario_probability in tree_node._cost_variable_datas:
                    if scenario_name == var_value.parent().name:
                        cost_variable_value = var_value

                if cost_variable_value is not None:
                    print("\tStage=%20s     Cost=%10.4f" % (stage._name, cost_variable_value))
                    cost = cost_variable_value
                else:
                    print("\tStage=%20s     Cost=%10s" % (stage._name, "Not Rprted."))
                    cost = 0.0
                aggregate_cost += cost

            print("\tTotal scenario cost=%10.4f" % aggregate_cost)
            print("")
        print("----------------------------------------------------")

from itertools import izip
from ..errors import *

__all__ = ['Filter', 'VarFilter', 'RuleManager', 'RuleSet']

class Filter(object):
    def __init__(self, default_controller=None):
        """
        rc_map is a mapping between the RuleController filter_value and the
        RuleController object. When the value parameter is called on a Filter 
        object it will return a value that will be used as the key of the rc_map 
        and thus will return the RuleController. 
        """
        self.default_controller = default_controller
        self.rc_map = {}      
    
    def value(self, row):
        """Default filter will return None for the filter value. This is 
        essentially not filtering anything
        """
        return None
    
    def filter(self, row):
        try:
            return self.rc_map[self.value(row)].transform(row)
        except KeyError:
            if self.default_controller:
                self.default_controller.transform(row)
    
class VarFilter(Filter):
    def __init__(self, filter_var, variables, default_contoller=None):
        Filter.__init__(self, default_contoller)
        self.filter_var = filter_var
        self.variables = variables
        self.validate()
        
    def validate(self):
        if self.filter_var not in self.variables:
            raise TransformError('filter_var must be in variables.')
        
    def value(self, row):
        return row[self.filter_var.name]
  
class RuleManager(object):
    """One Rule Manager for a RuleTaskManager. Can either select controller based on a filter, 
    or iterate over a list of controllers based on priority."""
    def __init__(self, metadata):
        self.metadata = metadata
        self.rc_list = []
            
    def add_rule_controller(self, controller):
        """Add a RuleController to a RuleManager. Every RuleManager
        must have at least one RuleController"""
        self.validate_controller(controller)
        if self.metadata.rule_filter:
            self.metadata.rule_filter.rc_map[controller.metadata.filter_value] = controller
        else:
            self.rc_list.append(controller)
        
    def validate_filter_controller(self, controller):
        if self.metadata.rule_filter:
            if controller.metadata.filter_value in self.metadata.rule_filter.rc_map:
                raise TransformError("Only one controller can be defined for a filter_value. %s already in rc_map." % controller.metadata.filter_value)
        if isinstance(controller, RuleSet):
            if len(controller.rules) == 0 and len(controller.regex_rules) == 0 and controller.metadata.missing is None and controller.metadata.unknown is None:
                raise TransformError("Must have at least one Rule or RegexRule in a RuleSet.")
    
    def task_func(self):
        def run_rules(row):
            if self.metadata.rule_filter: #if a filter is present use it to select the RuleController
                self.metadata.rule_filter.filter(row)
            else: #otherwise iterate over ruleConrollers in rc_list
                for controller in sorted(self.rc_list, key = lambda c: c.metadata.priority):
                    self.controller.transform(row)
                
        return run_rules

class RuleSet(object):
    def __init__(self, metadata):
        self.metadata = metadata
        self.rules = {}
        self.regex_rules = []
        
    def validate_rules(self):
        """
        1) A RuleSet can contain 0 or many RegexRules and 0 or many Rules.
           or
           A RuleSet can contain only one AllRule and no other rules.
           or
           A RuleSet can contain only one CopyRule and no other rules.
        """
        if self.metadata.all_rule and (len(self.rules) > 1 or len(self.regex_rules) > 0):
            raise TransformRuleError("Can not have AllRule and other rules.")
        if self.metadata.copy_rule and (len(self.rules) > 1 or len(self.regex_rules) > 0):
            raise TransformRuleError("Can not have CopyRule and other rules.")
        
    def validate_rule(self):
        pass
        #TODO: add validation that rule o_vars in resultset o_vars 
        
    def add_rule(self, rule):
        #TODO: exact rule could be not regex rule as long as exact is not math type
        if rule.metadata.type in ['search', 'match', 'exact']:
            if rule.initial not in self.regex_rules:
                self.regex_rules.append(rule)
            else:
                raise TransformRuleError("rule.initial already present in rules.")
        else:
            if rule.metadata.type == 'all':
                self.metadata.all_rule = True
            elif rule.metadata.type == 'copy':
                self.metadata.copy_rule = True
            if rule.initial not in self.rules:
                self.rules[rule.initial] = rule
            else:
                raise TransformRuleError("rule.initial already present in rules.")
                
        self.validate_rules()
        
    def transform(self, row):
        args = []
        kw = {}
        found_rule = False
        
        def _assign_row(out_vars, result):
            #o_vals is the list of output values returned from the rule.convert method
            for o_var, o_value in izip(out_vars, result):
                row[o_var.name] = o_value
            return True
        
        if self.metadata.all_rule:
            _assign_row(self.metadata.out_vars, self.rules[None].convert())
        else:      
            key = ''.join([str(row[v.name]) if row[v.name] is not None else '' for v in self.metadata.in_vars])
        
            if key == '':
                if self.metadata.missing: #if key is blank assign missing value
                    found_rule = _assign_row(self.metadata.out_vars, self.metadata.missing)
                    
                else:
                    return
            
            elif self.metadata.copy_rule:
                found_rule = _assign_row(self.metadata.out_vars,  self.rules[None].convert())
                match = True
            
            elif key in self.rules: #check to see if the key is in rules dict
                found_rule = _assign_row(self.rules[key].metadata.out_vars, self.rules[key].convert())
            
            elif self.regex_rules: #if key not found in rules dict then see if regex rule can handle the key
                for rule in self.regex_rules:
                    if rule.handle(key):
                        found_rule = _assign_row(rule.metadata.out_vars, rule.convert())
                        
            if not found_rule:
                if self.metadata.unknown:
                     #TODO add output to log file
                    found_rule = _assign_row(self.metadata.out_vars, self.metadata.unknown)
                else:
                    #TODO change this to output to log file            
                    raise ConvertError('Unable to convert key: %s' % key)
        
        
                    
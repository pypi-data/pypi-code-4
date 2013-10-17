import os, sys, unittest2, re
sys.path.append(os.path.join(__file__, '..', '..', '..', '..'))

#TODO: fix imports
from cardsharp.transform import *
from cardsharp.variables import *
from cardsharp.errors import *

class TestFilter(unittest2.TestCase):
    def setUp(self):
        self.filter = Filter()
        self.controller_meta = RuleControllerMetadata(1, Filter())
        self.rc = RuleManager(self.controller_meta)
        
    def test_init(self):
        self.assertEquals(self.filter.rc_map, {})
            
    def test_value(self):
        self.assertEquals(self.filter.value([1, 2]), None)
    
    def test_filter(self):
        self.filter.rc_map[self.rc.metadata.filter_value] = self.rc
        self.assertEquals(self.filter.filter([1,2]), None)
        
class TestVarFilter(unittest2.TestCase):
    def setUp(self):
        self.variables = VariableSet(['state', 'out'])
        self.filter = VarFilter(self.variables['state'], self.variables) #filter on state
        self.ruleset_meta = RuleSetMetadata(VariableSet(['a']), VariableSet(['out']), 'az', 1)
        self.rule_meta = RuleMetadata('', None, VariableSet(['a']), VariableSet(['out']))
        self.rule = Rule('1', [99], self.rule_meta)
        self.rc = RuleSet(self.ruleset_meta)
        self.rc.add_rule(self.rule)
        
    def test_init(self):
        self.assertEquals(self.filter.filter_var.name, 'state')
    
    def test_validate(self):
        self.filter.filter_var = Variable('a', 'string')
        self.assertRaises(TransformError, self.filter.validate)
    
    def test_value(self):
        self.assertEquals(self.filter.value({'state':'az', 'out':1}), 'az')
        self.assertEquals(self.filter.value({'state':'al', 'out':1}), 'al')
    
    def test_filter(self):
        self.filter.rc_map[self.rc.metadata.filter_value] = self.rc
        self.assertEquals(self.filter.filter({'state':'az', 'a':'1', 'out':1}), None) #TODO this should not work
        self.assertEquals(self.filter.filter({'state':'al', 'a':'1', 'out':1}), None)

class TestRuleSet(unittest2.TestCase):
    def setUp(self):
        self.ruleset_meta = RuleSetMetadata(VariableSet(['a']), VariableSet(['b', 'c']), 'az', 1)
        self.rs = RuleSet(self.ruleset_meta)
        self.rule_meta = RuleMetadata('None', None, VariableSet(['a']), VariableSet(['b', 'c']))
        self.rule = Rule('1', [2, '3'], self.rule_meta)
    
    def test_init(self):
        self.assertEquals(self.rs.metadata, self.ruleset_meta)
        self.assertEquals(self.rs.regex_rules, [])
        self.assertEquals(self.rs.rules, {})
    
    def test_add_rule(self):
        #test that when adding rule initial is stored as key and result is stored as value
        self.rs.add_rule(self.rule)
        self.assertEquals(self.rs.rules['1'].result, [2, '3'])
        #test that when adding search, match, exact rule they are added to regex_rules
        self.rule.metadata.type = 'search'
        self.rs.add_rule(self.rule)
        self.assertEquals(True, True if self.rule in self.rs.regex_rules else False)
        self.rule.metadata.type = 'match'
        self.rs.add_rule(self.rule)
        self.assertEquals(True, True if self.rule in self.rs.regex_rules else False)
        self.rule.metadata.type = 'exact'
        self.rs.add_rule(self.rule)
        self.assertEquals(True, True if self.rule in self.rs.regex_rules else False)
        #test that when adding all all_rule ruleset metadata has all_rule updated
        self.rule.metadata.type = 'all'
        self.rs.rules = {} 
        self.rs.regex_rules = []
        self.rs.add_rule(self.rule)
        self.assertEquals(self.rs.metadata.all_rule, True)
        #test that when all_rule is present no other rules can be added
        self.rule.initial = '2'
        self.assertRaises(TransformRuleError, self.rs.add_rule, (self.rule))
        #test that when adding copy_rule ruleset metadata has copy_rule updated
        self.rs.rules = {}
        self.rule.metadata.type = 'copy'
        self.rs.add_rule(self.rule)
        self.assertEquals(self.rs.metadata.copy_rule, True)
        #test that when copy_rule is present no other rules can be added
        self.rule.initial = 'a'
        self.assertRaises(TransformRuleError, self.rs.add_rule, (self.rule))
                
    def test_task_func_all_rule(self):
        #test all rule
        row = {'a':1, 'b':None, 'c':None}
        self.rule.metadata.type = 'all'
        self.rule.initial = None
        self.rs.add_rule(self.rule)
        self.rs.transform(row)
        self.assertEquals(row, {'a':1, 'b':2, 'c':'3'})
    
    def test_task_func_missing(self):
        #test missing metadata
        self.rs.metadata.missing = [None, None]
        row = {'a':None, 'b':1, 'c':2}
        self.rs.transform(row)
        self.assertEquals(row, {'a':None, 'b':None, 'c':None})
    
    def test_task_func_copy_rule(self):
        #test copy rule
        self.rule.metadata.type = 'copy'
        self.rule.initial = None
        self.rule.result = 'a'
        self.rs.add_rule(self.rule)
        row = {'a':None, 'b':1, 'c':2}
        self.rs.metadata.missing = [None, None]
        self.rs.transform(row) #None rule should still work
        self.assertEquals(row, {'a':None, 'b':None, 'c':None})
        self.rule.metadata.missing = None
        row = {'a':None, 'b':1, 'c':2}
        self.rs.transform(row)
        self.assertEquals(row, {'a':None, 'b':None, 'c':None})
        row = {'a':0, 'b':0, 'c':0}
        self.assertEquals(row, {'a':0, 'b':0, 'c':0})
    
    def test_task_func_rule(self):
        #test missing metadata
        self.rs.metadata.missing = [None, None]
        self.rs.add_rule(self.rule)
        row = {'a':None, 'b':1, 'c':2}
        self.rs.transform(row)
        self.assertEquals(row, {'a':None, 'b':None, 'c':None}) #none rule should still work
        row = {'a':1, 'b':1, 'c':2}
        self.rs.transform(row)
        self.assertEquals(row, {'a':1, 'b':2, 'c':'3'}) 
    
    def test_task_func_regex_rule(self):
        self.rule_meta.type = 'search'
        self.search_re_rule = RegexRule('abc.', ['2', '3'], self.rule_meta)
        self.rs.add_rule(self.search_re_rule)
        row = {'a':'asdas abc. asdasd', 'b':1, 'c':2}
        self.rs.transform(row)
        self.assertEquals(row, {'a':'asdas abc. asdasd', 'b':'2', 'c':'3'})
        
    def test_task_func_unknown(self):
        #test unknown metadata
        self.rs.rules = {}
        self.rs.metadata.unknown = [9, 9]
        row = {'a':10, 'b':1, 'c':2}
        self.rs.transform(row)
        self.assertEquals(row, {'a':10, 'b':9, 'c':9})
        #test convertError when no unknown value specified
        self.rs.metadata.unknown = None
        row = {'a':10, 'b':1, 'c':2}
        self.assertRaises(ConvertError, self.rs.transform, row)
        
#class TestRuleManager(unittest2.TestCase):
#    def setUp(self):
#        self.manager_meta = RuleManagerMetadata()
#        self.controller_meta = RuleControllerMetadata(1, 'az')
#        self.rm = RuleManager(self.manager_meta)
#        self.rc = RuleController(self.controller_meta)
#        self.ruleset_meta = RuleSetMetadata(VariableSet(['a', 'b', 'c']), VariableSet(['d', 'e', 'f']), 'az', 1)
#        self.rs = RuleSet(self.ruleset_meta)
#        
#    def test_init(self):
#        self.assertEquals(self.rm.metadata, self.manager_meta)
#    
#    def test_add_rule_controller(self):
#        self.rm.add_rule_controller(self.rc)
#        self.assertEquals(self.rm.metadata.rule_filter.rc_map['az'], self.rc)
#        
#    def test_validate_controller(self):
#        self.assertRaises(TransformError, self.rm.add_rule_controller, (self.rc))
#        self.assertRaises(TransformError, self.rm.add_rule_controller, (self.rs))
#    
#    def test_task_func(self):
#        pass
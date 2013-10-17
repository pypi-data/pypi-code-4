import os, sys, unittest2
sys.path.append(os.path.join(__file__, '..', '..', '..', '..'))

from cardsharp.transform import * 
from cardsharp.variables import *
from cardsharp.errors import *

__all__ = ['TestRuleMetadata', 'TestRuleSetMetadata']

class TestRuleMetadata(unittest2.TestCase):
    def setUp(self):
        key_vars = VariableSet(['a', 'b', 'c'])
        value_vars = VariableSet(['d', 'e', 'f'])
        log = 'abc' #change this to a log
        type = 'none'
        escape = True
        opt = {'missing':[None,None,None], 'unknown': [None, None, None], 'log':'abc', 'priority':1}
        self.rule_meta = RuleMetadata(type, escape, key_vars, value_vars, **opt)
                
    def test_init(self):
        self.assertEqual(self.rule_meta.type, 'none')
        self.assertEqual(self.rule_meta.escape, True)
        self.assertEqual(self.rule_meta.key_meta['a'].name, 'a')
        self.assertEqual(self.rule_meta.out_vars['e'].name, 'e')
        self.assertEqual(self.rule_meta.keywords.get('missing'), [None, None, None])
        self.assertEqual(self.rule_meta.keywords.get('unknown'), [None, None, None])
        self.assertEqual(self.rule_meta.keywords.get('log'), 'abc')
        self.assertEqual(self.rule_meta.all_rule, False)
        self.assertEqual(self.rule_meta.copy_rule, False)
        self.assertEqual(self.rule_meta.priority, 1)
        self.rule_meta.missing = [1,2]
        self.assertRaises(TransformRuleError, RuleMetadata.validate, (self.rule_meta))
        self.rule_meta.missing = [1,2,3]
        self.rule_meta.unknown = [1,2]
        self.assertRaises(TransformRuleError, RuleMetadata.validate, (self.rule_meta))
    
class TestRuleManagerMetadata(unittest2.TestCase):
    def setUp(self):
        self.f = Filter()
        self.manager_meta = RuleManagerMetadata(1, self.f)
        
    def test_init(self):
        self.assertEqual(self.manager_meta.priority, 1)
        self.assertEqual(self.manager_meta.rule_filter, self.f)
        self.manager_meta.rule_filter = 'f'
        self.assertRaises(TransformError, self.manager_meta.validate)

class TestRuleControllerMetadata(unittest2.TestCase):
    def setUp(self):
        self.f = Filter()
        self.manager_meta = RuleManagerMetadata(1, self.f)
        
    def test_init(self):
        self.assertEqual(self.manager_meta.priority, 1)
        self.assertEqual(self.manager_meta.rule_filter, self.f)
        self.manager_meta.rule_filter = 'f'
        self.assertRaises(TransformError, self.manager_meta.validate)

class TestKeyMetadata(unittest2.TestCase):
    def setUp(self):
        self.var = Variable('a')
        self.trans_func = lambda x: x.lower()
        kw = {'inner_trim':True,
              'as_str':True,
              'transform': self.trans_func}
        
        self.key_meta = KeyMetadata(self.var, 1, **kw)
        
    def test_init(self):
        self.assertEqual(self.key_meta.name, 'a')
        self.assertEqual(str(self.key_meta.format),'string')
        self.assertEqual(self.key_meta.as_str, True)
        self.assertEqual(self.key_meta.inner_trim, True)
        self.assertEqual(self.key_meta.transform('TEST'), 'test')
        
        self.key_meta = KeyMetadata(self.var, 1)
        self.assertEqual(self.key_meta.name, 'a')
        self.assertEqual(str(self.key_meta.format), 'string')
        self.assertEqual(self.key_meta.as_str, False)
        self.assertEqual(self.key_meta.inner_trim, False)
        self.assertEqual(self.key_meta.transform('TEST'), 'TEST')
    
    def test_get_key(self):
        self.assertEqual(self.key_meta.get_key({'a':'1'}), '1')
        self.assertEqual(self.key_meta.get_key({'a':'TT'}), 'tt')
        self.assertEqual(self.key_meta.get_key({'a':'  T   T  '}), 't t')
        self.assertEqual(self.key_meta.get_key({'a':None}), '')
    
class TestRuleSetMetadata(unittest2.TestCase):
    def setUp(self):
        key_vars = VariableSet(['a', 'b', 'c'])
        value_vars = VariableSet(['d', 'e', 'f'])
        log = 'abc' #change this to a log
        missing = -1
        unkown = 9
        self.ruleset_meta = RuleSetMetadata(key_vars, value_vars, None, 1, **{'missing':[-1,-1,-1], 'unknown':[9,9,9], 'log':log})
        
    def tearDown(self):
        del self.ruleset_meta
        
    def test_init(self):
        self.assertEqual(self.ruleset_meta.key_meta['a'].name, 'a')
        self.assertEqual(self.ruleset_meta.out_vars['e'].name, 'e')
        self.assertEqual(self.ruleset_meta.filter_value, None)
        self.assertEqual(self.ruleset_meta.priority, 1)
        self.assertEqual(self.ruleset_meta.missing, [-1, -1, -1])
        self.assertEqual(self.ruleset_meta.unknown, [9,9,9])
        self.assertEqual(self.ruleset_meta.log, 'abc')
        self.assertEqual(self.ruleset_meta.all_rule, False)
        self.assertEqual(self.ruleset_meta.copy_rule, False)
        self.assertEqual(self.ruleset_meta.force_unknown, False)
        self.ruleset_meta.missing = [1,2]
        self.assertRaises(TransformRuleError, RuleSetMetadata.validate, (self.ruleset_meta))
        self.ruleset_meta.missing = [1,2,3]
        self.ruleset_meta.unknown = [1,2]
        self.assertRaises(TransformRuleError, RuleSetMetadata.validate, (self.ruleset_meta))
            
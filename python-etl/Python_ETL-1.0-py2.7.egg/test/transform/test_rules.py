import os, sys, unittest2
sys.path.append(os.path.join(__file__, '..', '..', '..', '..'))

from cardsharp.transform import * 
from cardsharp.variables import *
from cardsharp.errors import *

import re

class TestRule(unittest2.TestCase):
    def setUp(self):
        self.rule_meta = RuleMetadata(None, None, VariableSet(['a']), VariableSet(['b', 'c']))
        self.rule = Rule('a', ['2', '3'], self.rule_meta)
    
    def test_init(self):
        self.assertEquals(self.rule.initial, 'a')
        self.assertEquals(self.rule.result, ['2', '3'])
        self.assertEquals(self.rule.metadata, self.rule_meta)
    
    def test_validate(self):
        self.rule.initial = None
        self.assertRaises(TransformRuleError, Rule.validate, self.rule)
    
    def test_convert(self):
        self.assertEquals(self.rule.convert(), ['2', '3'])
        
class TestCopyRule(unittest2.TestCase):
    def setUp(self):
        self.rule_meta = RuleMetadata(None, None, VariableSet(['a']), VariableSet(['b', 'c']))
        self.rule = CopyRule(['2', '3'], self.rule_meta)
        
    def test_init(self):
        self.assertEquals(self.rule.initial, None)
        self.assertEquals(self.rule.result, ['2', '3'])
        self.assertEquals(self.rule.metadata, self.rule_meta)
    
    def test_validate(self):
        self.rule.metadata.key_meta = VariableSet(['b', 'c'])
        self.assertRaises(TransformRuleError, CopyRule.validate, self.rule)
    
    def test_convert(self):
        self.assertEquals(self.rule.convert({'a':1}), [1,1])
    
class TestRegexRule(unittest2.TestCase):
    def setUp(self):
        self.rule_meta = RuleMetadata(None, None, VariableSet(['a']), VariableSet(['b', 'c']))
        self.rule_meta.type = 'search'
        self.search_re_rule = RegexRule('abc.', ['2', '3'], self.rule_meta)
        self.rule_meta.type = 'match'
        self.match_re_rule = RegexRule('abc.', ['2', '3'], self.rule_meta)
        self.rule_meta.type = 'exact'
        self.exact_re_rule = RegexRule('abc.', ['2', '3'], self.rule_meta)
        self.rule_meta.escape = True
        self.exact_re_rule_e = RegexRule('abc.', ['2', '3'], self.rule_meta)
        self.rule_meta.type = 'search'
        self.search_re_rule_e = RegexRule('abc.', ['2', '3'], self.rule_meta)
        self.rule_meta.type = 'match'
        self.match_re_rule_e = RegexRule('abc.', ['2', '3'], self.rule_meta)
        
    def test_init(self):
        for r in [self.exact_re_rule, self.exact_re_rule_e, self.match_re_rule,
                  self.match_re_rule_e, self.search_re_rule, self.search_re_rule_e]:
            self.assertEquals(r.initial, 'abc.')
            self.assertEquals(r.result, ['2', '3'])
            self.assertEquals(r.metadata, self.rule_meta)
        
        #test exact
        self.assertEquals(self.exact_re_rule.re_func, re.match)
        self.assertEquals(self.exact_re_rule_e.re_func, re.match)
        self.assertEquals(self.exact_re_rule.regex.pattern, 'abc.$')
        self.assertEquals(self.exact_re_rule_e.regex.pattern, 'abc\.$')
        
        #test search
        self.assertEquals(self.search_re_rule.re_func, re.search)
        self.assertEquals(self.search_re_rule_e.re_func, re.search)
        self.assertEquals(self.search_re_rule.regex.pattern, 'abc.')
        self.assertEquals(self.search_re_rule_e.regex.pattern, 'abc\.')
        
        #test match
        self.assertEquals(self.exact_re_rule.re_func, re.match)
        self.assertEquals(self.exact_re_rule_e.re_func, re.match)
        self.assertEquals(self.match_re_rule.regex.pattern, 'abc.')
        self.assertEquals(self.match_re_rule_e.regex.pattern, 'abc\.')
        
    def test_validate(self):
        self.exact_re_rule.metadata.type = None
        self.assertRaises(TransformRuleError, RegexRule.validate, self.exact_re_rule)
    
    def test_handle(self):
        #test match
        self.assertEquals(True, True if self.match_re_rule.handle('abc1 asd') else False)
        self.assertEquals(False, True if self.match_re_rule.handle('1abc1 asd') else False)
        self.assertEquals(True, True if self.match_re_rule_e.handle('abc. sd') else False)
        self.assertEquals(False, True if self.match_re_rule_e.handle('abc1 sd') else False)
        
        #test search
        self.assertEquals(True, True if self.search_re_rule.handle('as abc1 asd') else False)
        self.assertEquals(False, True if self.search_re_rule.handle('asd ac df') else False)
        self.assertEquals(True, True if self.search_re_rule_e.handle('asdabc.dasda') else False)
        self.assertEquals(False, True if self.search_re_rule_e.handle('asd abc1 asd') else False)
        
        #test exact
        self.assertEquals(True, True if self.exact_re_rule.handle('abc1') else False)
        self.assertEquals(False, True if self.exact_re_rule.handle('abc1s') else False)
        self.assertEquals(True, True if self.exact_re_rule_e.handle('abc.') else False)
        self.assertEquals(False, True if self.exact_re_rule_e.handle('abc.1') else False)

class QucikTest(unittest2.TestCase):
    def setUp(self):
        self.rule_meta = RuleMetadata('search', None, VariableSet(['a']), VariableSet(['b', 'c']))
        self.re_math_rule = RegexMathRule('(\d+)a#b(\d+)c.', ['2.1', '#1'], self.rule_meta)
        self.rule_meta.escape = True
    
    def test_convert(self):
        self.re_math_rule.handle('02012a#b5c1')
        self.assertEquals(self.re_math_rule.convert(), [219.15, 12])

class QucikTest(unittest2.TestCase):
    def setUp(self):
        from cardsharp.util import *
        print calc('2,100+10')
        self.rule_meta = RuleMetadata('search', None, VariableSet(['a']), VariableSet(['b', 'c']))
        self.re_math_rule = RegexMathRule('(?<!susp )(#\d+|\d+),(\d+) mo jail[ ]*(?!susp)', ['#1,#2', '#1(365.25/12)', '99899899.88', '99999999.99', '99999999.99', 'None'], self.rule_meta)
        self.rule_meta.escape = True
    
    def test_convert(self):
        self.re_math_rule.handle('2,1 mo jail')
        self.assertEquals(self.re_math_rule.convert(), [21, 60.875, 99899899.88, 99999999.99, 99999999.99, None])

class TestRegexMathRule(unittest2.TestCase):
    def setUp(self):
        self.rule_meta = RuleMetadata('search', None, VariableSet(['a']), VariableSet(['b', 'c']))
        self.re_math_rule = RegexMathRule('(\d+)a#bc.', ['#1', '#1+12'], self.rule_meta)
        self.rule_meta.escape = True
        self.re_math_rule_e = RegexMathRule('#abc.', ['#1.#1(2)', '#1+12'], self.rule_meta)
        self.re_math_rule_err_1 = RegexMathRule('#abc.', ['#2', '#1+12'], self.rule_meta)
        self.re_math_rule_err_2 = RegexMathRule('#abc.', ['#1', '#1 12'], self.rule_meta)
        self.rule_meta_1 = RuleMetadata('search', None, VariableSet(['a']), VariableSet(['b', 'c', 'd', 'e', 'f', 'i', 'q']))
        self.rule_meta_1.escape = True
        self.re_math_rule_test = RegexMathRule('#/#/#,judgment on plea of guilty,incarc:#d,susp:#d,fine:$#', [38, 4, '#4', 99899899.88, 99999999.99, 99999999.99, 99999999.99], self.rule_meta_1)
        
    def test_init(self):
        self.assertEquals(self.re_math_rule.regex.pattern, '(\d+)a#bc.')
        self.assertEquals(self.re_math_rule_e.regex.pattern, '(\d+|#\d+|#)abc\.')
        
    def test_handle(self):
        self.assertEquals(True, True if self.re_math_rule.handle('12a#bc1') else False)
        self.assertEquals(True, True if self.re_math_rule.groups == ('12',) else False)
        self.re_math_rule.groups = None #reset groups 
        self.assertEquals(False, True if self.re_math_rule.handle('a#bc1s') else False)
        self.assertEquals(False, True if self.re_math_rule.groups else False)
        #test escape
        self.assertEquals(True, True if self.re_math_rule_e.handle('12abc.') else False)
        self.assertEquals(True, True if self.re_math_rule_e.groups == ('12',) else False)
        self.re_math_rule_e.groups = None #reset groups 
        self.assertEquals(False, True if self.re_math_rule_e.handle('abc.') else False)
        self.assertEquals(False, True if self.re_math_rule_e.groups else False) 
        self.assertEquals(True, True if self.re_math_rule_test.handle('3/24/1992,judgment on plea of guilty,incarc:365d,susp:245d,fine:$1000') else False)
        
    def test_convert(self):
        self.re_math_rule.handle('12a#bc1')
        self.assertEquals(self.re_math_rule.convert(), [12, 24])
        self.re_math_rule_e.handle('12abc.')
        self.assertEquals(self.re_math_rule_e.convert(), [24.24, 24])
        
        self.re_math_rule_err_1.handle('12abc.')
        self.assertRaises(TransformRuleError, self.re_math_rule_err_1.convert)
        self.re_math_rule_err_2.handle('12abc.')
        self.assertRaises(TransformRuleError, self.re_math_rule_err_2.convert)
        self.re_math_rule_test.handle('3/24/1992,judgment on plea of guilty,incarc:365d,susp:245d,fine:$1000')
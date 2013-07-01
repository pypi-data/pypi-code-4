import unittest

from parsimonious.nodes import Node, RegexNode

import csp_validator.csp

class TestCSPGrammar(unittest.TestCase):

    def test_basic_default_src_star(self):
        policy = "default-src *"
        dname = "default-src"
        policy_len = len(policy)
        dname_len = len(dname)
        expected = Node('policy', policy, 0, policy_len, children=[
            Node('directive_name', dname, 0, dname_len, children=[
             Node('', dname, 0, dname_len)]),
            Node('space', " ", dname_len, dname_len+1),
            Node('', '*', dname_len+1, dname_len+2, children=[
             Node('directive_value', '*', dname_len+1, dname_len+2, children=[
              Node('', '*', dname_len+1, dname_len+2)]),
             Node('', '', dname_len+2, dname_len+2)]),
            Node('', '', dname_len+2, dname_len+2)])
        
        actual = csp_validator.csp.parse('default-src *')
        self.assertEqual(repr(actual), repr(expected))

class TestCSPValidation(unittest.TestCase):
    def test_basic_default_src_star(self):
        policy = "default-src *"
        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ['default-src *'])
        self.assertEqual(warnings, [])
        self.assertEqual(errors, [])

    def test_basic_default_src_error(self):
        policy = "default-src **"
        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ['default-src **'])
        self.assertEqual(warnings, [])
        self.assertEqual(errors, [("default-src **", "'*' (line 1, column 14) does not match CSP grammar.")])

    def test_basic_default_src_warning(self):
        policy = "default-src * https:" # doesn't make sense whatsoever...
        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ['default-src * https:'])
        self.assertEqual(warnings, [('default-src * https:', \
            "When %s is present, other values cannot be present as well." % "*")])

    def test_multiple_policies(self):
        policy = "default-src *; img-src google.com; script-src google.com"
        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ["default-src *", "img-src google.com", "script-src google.com"])
        self.assertEqual(warnings, [])
        self.assertEqual(errors, [])

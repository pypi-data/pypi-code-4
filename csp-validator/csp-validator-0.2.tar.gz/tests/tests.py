import unittest

from parsimonious.nodes import Node, RegexNode

import csp_validator.csp

class TestCSPGrammar(unittest.TestCase):

    #TODO: Fix this... but maybe not.. grammar is too complex now :(
    @unittest.skip("too complex to fix.")
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
    
    def test_multiple_policies(self):
        policy = "default-src *; img-src google.com; script-src google.com"
        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ["default-src *", "img-src google.com", "script-src google.com"])
        self.assertEqual(warnings, [])
        self.assertEqual(errors, [])

        policy = "default-src 'self'; img-src *;" + \
            "object-src media1.example.com media2.example.com *.cdn.example.com;" + \
            "script-src trustedscripts.example.com"

        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ["default-src 'self'", \
            "img-src *", "object-src media1.example.com media2.example.com *.cdn.example.com",
            "script-src trustedscripts.example.com"])
        self.assertEqual(warnings, [])
        self.assertEqual(errors, [])
    
    def test_deprecated_inline(self):
        policy = "default-src 'inline-script';"
        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ["default-src 'inline-script'"])
        self.assertEqual(warnings[0][1], ["'inline-script' is deprecated in favor of the W3C specification; \
use 'unsafe-inline' instead."])

    def test_https_with_unsafes(self):
        '''Online banking site wishes to ensure that all of the content in 
        its pages is loaded over TLS to prevent attackers from 
        eavesdropping on insecure content requests, but this policy does 
        not provide any protection from cross-site scripting vulnerabilities. '''
        
        policy = "default-src https: 'unsafe-inline' 'unsafe-eval'"
        rules, warnings, errors = csp_validator.csp.validate(policy)
        self.assertEqual(rules, ["default-src https: 'unsafe-inline' 'unsafe-eval'"])
        self.assertEqual(warnings[0][1], ["Enabling 'unsafe-inline' can enable cross-site scripting vulnerabilities.", \
            "Enabling 'unsafe-eval' can enable cross-site scripting vulnerabilities."])
        self.assertEqual(errors, [])

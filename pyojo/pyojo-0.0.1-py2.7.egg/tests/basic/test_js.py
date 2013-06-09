# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
from base import main, BasicTestCase
from pyojo.func import nolf
import pyojo.js as js

EXAMPLE = "alert('Test');"


class js_1_js_code(BasicTestCase):        
    """ Javascript generation functions.
    """
    
    def check(self, test):
        for item, expected in test:
            code = js.js_code(item)
            self.assertEqual(code, expected)
            self.assertIsInstance(code, basestring)


    def test_1(self):
        " Basic js_code conversions"
        test = [("", "''"),
                ("A", "'A'"),
                ("á", "'á'"),
                (1, "1"),
                (True, "true"),
                (False, "false"),
                (None, "null"),
                (js.Var("A"), "A"),
                (js.Code("A"), "A")]
        self.check(test)


    def test_2(self):
        " List js_code conversions"
        test = [([], "[]"),
                (["A", 1], "['A', 1]")]
        self.check(test)            


    def test_3(self):
        " Dictionary js_code conversions"
        test = [({}, "{}"),
                ({"A":"A"}, "{'A': 'A'}"),
                ({"A":js.Var("B")}, "{'A': B}"),
                ({js.Var("A"):"B"}, "{A: 'B'}")]
        self.check(test)


    def test_4(self):
        " Dictionary js_dict conversions"
        self.assertEqual(js.js_dict({"A":"A"}, False), "{'A': 'A'}")
        self.assertEqual(js.js_dict({"A":"A"}, True), "{A: 'A'}")
        self.assertEqual(js.js_dict({js.Var("A"):js.Var("B")}), "{A: B}")
        


class js_2_Var(BasicTestCase):
                
    def test_1(self):
        " Var.name"
        var = js.Var("A")
        self.assertEqual(var.var.code(),"A")
        self.assertEqual(var.code(),"A")


    def test_2(self):
        " Var.name errors"
        self.assertRaises(js.JavascriptError, js.Var, 1)


    def test_3(self):
        " Var.value integer"
        var = js.Var("A", 1)
        self.assertEqual(var.value, 1)
        self.assertEqual(var.code(),"var A = 1;")


    def test_4(self):
        " Var.value string"
        var = js.Var("A", "1")
        self.assertEqual(var.value, "1")
        self.assertEqual(var.code(),"var A = '1';")


class js_3_Code(BasicTestCase):
                
    def test_1(self):
        " Simple string"
        assert js.Code(EXAMPLE).code()==EXAMPLE


class js_4_Function(BasicTestCase):
                
    def test_1(self):
        self.assertIsInstance(js.Function(), js.Code)
        self.assertIsInstance(js.Function().code(), basestring)
        
    def test_2(self):
        " Function parameters"
        self.assertEqual(js.Function().code(), 
                         "function() {}")
        self.assertEqual(js.Function("X").code(), 
                         "function() {X}")
        self.assertEqual(js.Function("a", "X").code(), 
                         "function(a) {X}")
        self.assertEqual(js.Function("a", "b", "X").code(), 
                         "function(a, b) {X}")

    def test_3(self):
        " Function code"
        self.assertEqual(js.Function(js.Function()).code(), 
                         "function() {function() {}}")
        
        func = js.Function()
        self.assertEqual(js.Function([func, func]).code(), 
                         "function() {"+func.code()*2+"}")
        

        
   
# ----------------------------------------------------------------------------
        
if __name__=='__main__': 
    main()

# ----------------------------------------------------------------------------
